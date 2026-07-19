# kivyfn/runtime/process/manager.py
from __future__ import annotations

from logging.handlers import QueueListener
from multiprocessing import get_context
from multiprocessing.context import SpawnContext
from queue import Empty
from threading import Event, RLock, Thread
from time import monotonic, sleep
from typing import Any

from kivyfn.config.logging import FnLoggingConfig
from kivyfn.logging import get_logger
from kivyfn.logging.multiprocessing import create_queue_listener
from kivyfn.runtime.process.entry import process_entry
from kivyfn.runtime.process.message import (
    ProcessFailedMessage,
    ProcessReadyMessage,
)
from kivyfn.runtime.process.process import FnProcess
from kivyfn.runtime.process.types import (
    ProcessArgs,
    ProcessExitCallback,
    ProcessFailedCallback,
    ProcessKwargs,
    ProcessLogQueue,
    ProcessReadyCallback,
    ProcessStatusQueue,
    ProcessTarget,
)


logger = get_logger(__name__)


class FnProcessManager:
    def __init__(
        self,
        logging_config: FnLoggingConfig,
    ) -> None:
        self._context: SpawnContext = get_context("spawn")

        self._log_queue: ProcessLogQueue = self._context.Queue()
        self._log_listener: QueueListener = create_queue_listener(
            self._log_queue,
            logging_config,
        )
        self._log_listener.start()

        self._processes: dict[str, FnProcess] = {}
        self._status_queue: ProcessStatusQueue | None = None
        self._listener_thread: Thread | None = None
        self._listener_stop = Event()
        self._lock = RLock()

    @property
    def registered(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._processes)

    @property
    def running(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(
                name
                for name, process in self._processes.items()
                if process.running
            )

    def __contains__(self, name: str) -> bool:
        with self._lock:
            return name in self._processes

    def register(
        self,
        name: str,
        target: ProcessTarget,
        *,
        on_ready: ProcessReadyCallback | None = None,
        on_failed: ProcessFailedCallback | None = None,
        on_exit: ProcessExitCallback | None = None,
    ) -> FnProcess:
        if not isinstance(name, str) or not name:
            raise ValueError(
                "Process name must be a non-empty string"
            )

        with self._lock:
            if name in self._processes:
                raise ValueError(
                    f"Process {name!r} is already registered"
                )

            process = FnProcess(
                name=name,
                target=target,
                on_ready=on_ready,
                on_failed=on_failed,
                on_exit=on_exit,
            )

            self._processes[name] = process
            return process

    def unregister(self, name: str) -> None:
        process = self.get(name)

        if process.running:
            raise RuntimeError(
                f"Cannot unregister running process {name!r}"
            )

        with self._lock:
            self._processes.pop(name, None)

    def get(self, name: str) -> FnProcess:
        with self._lock:
            try:
                return self._processes[name]
            except KeyError:
                raise KeyError(
                    f"Process {name!r} is not registered"
                ) from None

    def start(
        self,
        name: str,
        args: ProcessArgs = (),
        kwargs: ProcessKwargs | None = None,
        *,
        wait: bool = False,
        timeout: float | None = None,
        daemon: bool = True,
    ) -> FnProcess:
        process = self.get(name)

        if process.running:
            raise RuntimeError(
                f"Process {name!r} is already running"
            )

        self._ensure_listener()

        if self._status_queue is None:
            raise RuntimeError(
                "Process status queue was not initialized"
            )

        launch_kwargs = (
            {}
            if kwargs is None
            else dict(kwargs)
        )
        stop_event = self._context.Event()
        native_process = self._context.Process(
            name=name,
            target=process_entry,
            args=(
                process.name,
                process.target,
                args,
                launch_kwargs,
                self._status_queue,
                stop_event,
                self._log_queue,
            ),
        )
        native_process.daemon = daemon

        process._prepare(
            native_process=native_process,
            stop_event=stop_event,
        )

        try:
            native_process.start()
        except BaseException:
            process._reset()
            raise

        if wait:
            self._wait_until_ready(
                process,
                timeout=timeout,
            )

        return process

    def stop(
        self,
        name: str,
        *,
        timeout: float | None = 5.0,
        kill_timeout: float | None = 1.0,
    ) -> None:
        process = self.get(name)
        native_process = process._native_process

        if native_process is None or process.exited:
            return

        process._mark_stopping()
        native_process.join(timeout)

        if native_process.is_alive():
            native_process.terminate()
            native_process.join(kill_timeout)

        if native_process.is_alive():
            native_process.kill()
            native_process.join()

        self._scan_exits()

    def terminate(
        self,
        name: str,
        *,
        timeout: float | None = 1.0,
    ) -> None:
        process = self.get(name)
        native_process = process._native_process

        if native_process is None or not native_process.is_alive():
            return

        process._mark_stopping()
        native_process.terminate()
        native_process.join(timeout)
        self._scan_exits()

    def kill(self, name: str) -> None:
        process = self.get(name)
        native_process = process._native_process

        if native_process is None or not native_process.is_alive():
            return

        process._mark_stopping()
        native_process.kill()
        native_process.join()
        self._scan_exits()

    def stop_all(
        self,
        *,
        timeout: float | None = 5.0,
        kill_timeout: float | None = 1.0,
    ) -> None:
        with self._lock:
            names = tuple(self._processes)

        for name in names:
            self.stop(
                name,
                timeout=timeout,
                kill_timeout=kill_timeout,
            )

    def shutdown(
        self,
        *,
        timeout: float | None = 5.0,
        kill_timeout: float | None = 1.0,
    ) -> None:
        self.stop_all(
            timeout=timeout,
            kill_timeout=kill_timeout,
        )

        self._listener_stop.set()

        if self._listener_thread is not None:
            self._listener_thread.join(timeout=1.0)

        if self._status_queue is not None:
            close = getattr(
                self._status_queue,
                "close",
                None,
            )

            if callable(close):
                close()

        self._listener_thread = None
        self._status_queue = None

        self._log_listener.stop()

    def _ensure_listener(self) -> None:
        if (
            self._listener_thread is not None
            and self._listener_thread.is_alive()
        ):
            return

        self._listener_stop.clear()
        self._status_queue = self._context.Queue()
        self._listener_thread = Thread(
            target=self._listen,
            name="fn-process-listener",
            daemon=True,
        )
        self._listener_thread.start()

    def _listen(self) -> None:
        while not self._listener_stop.is_set():
            self._receive_message()
            self._scan_exits()

        self._scan_exits()

    def _receive_message(self) -> None:
        if self._status_queue is None:
            return

        try:
            message: Any = self._status_queue.get(
                timeout=0.1
            )
        except Empty:
            return
        except (EOFError, OSError):
            if not self._listener_stop.is_set():
                logger.exception(
                    "Process listener could not read "
                    "the status queue"
                )

            return

        try:
            self._dispatch(message)
        except BaseException:
            logger.exception(
                "Process listener failed to dispatch "
                "a lifecycle message"
            )

    def _dispatch(self, message: Any) -> None:
        if isinstance(message, ProcessReadyMessage):
            process = self.get(message.process)
            process._mark_ready(message.payload)
            return

        if isinstance(message, ProcessFailedMessage):
            process = self.get(message.process)
            process._mark_failed(message.error)
            return

        logger.warning(
            "Ignored unknown process lifecycle message: %r",
            message,
        )

    def _scan_exits(self) -> None:
        with self._lock:
            processes = tuple(
                self._processes.values()
            )

        for process in processes:
            native_process = process._native_process

            if native_process is None:
                continue

            if native_process.pid is None:
                continue

            if process.exited or native_process.is_alive():
                continue

            process._mark_exited(
                native_process.exitcode
            )

    @staticmethod
    def _wait_until_ready(
        process: FnProcess,
        timeout: float | None,
    ) -> None:
        started_at = monotonic()

        while True:
            if process.ready:
                return

            if process.failure is not None:
                raise RuntimeError(
                    f"Process {process.name!r} failed "
                    "during startup: "
                    f"{process.failure.message}"
                )

            if process.exited:
                raise RuntimeError(
                    f"Process {process.name!r} exited "
                    "before reporting readiness with "
                    f"exit code {process.exitcode}"
                )

            if (
                timeout is not None
                and monotonic() - started_at >= timeout
            ):
                raise TimeoutError(
                    f"Process {process.name!r} did not "
                    "report readiness within "
                    f"{timeout} seconds"
                )

            sleep(0.01)
