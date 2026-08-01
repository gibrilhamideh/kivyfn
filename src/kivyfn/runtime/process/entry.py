# kivyfn/runtime/process/entry.py
from __future__ import annotations

import asyncio
import signal

from kivyfn.logging import get_logger
from kivyfn.logging.multiprocessing import configure_process_logging
from kivyfn.runtime.process.context import FnProcessContext
from kivyfn.runtime.process.types import (
    ProcessArgs,
    ProcessKwargs,
    ProcessLogQueue,
    ProcessStatusQueue,
    ProcessStopEvent,
    ProcessTarget,
)


logger = get_logger(__name__)


def process_entry(
    name: str,
    target: ProcessTarget,
    args: ProcessArgs,
    kwargs: ProcessKwargs,
    status_queue: ProcessStatusQueue,
    stop_event: ProcessStopEvent,
    log_queue: ProcessLogQueue,
) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    configure_process_logging(log_queue)

    context = FnProcessContext(
        name=name,
        args=args,
        kwargs=kwargs,
        status_queue=status_queue,
        stop_event=stop_event,
    )

    try:
        target(context)
    except asyncio.CancelledError:
        return
    except BaseException as error:
        try:
            context.failed(error)
        except Exception:
            logger.exception("Failed to report process %r error", name)

        logger.exception("Process %r failed", name)
        raise
