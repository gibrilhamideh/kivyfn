"""
Register FnKivy-ui widgets to use without import.
"""

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType

from kivy.base import Builder
from kivy.factory import Factory
from kivy.uix.widget import Widget

def register():

    Builder.load_string(
        """
        #: import Animation kivy.animation.Animation
        #: import RelativeLayout kivy.uix.relativelayout.RelativeLayout
        #: import Factory kivy.factory.Factory
        #: import I18nRef kivyfn.i18n.ref.I18nRef

    """
    )

def load_kv(file: str):
    kv_path = Path(file).with_suffix(".kv")

    if not kv_path.exists():
        raise FileNotFoundError(
            f"KV file not found: {kv_path}"
        )

    Builder.load_file(str(kv_path))

def discover_widgets(
    root: Path,
) -> None:
    # TODO: REMOVE THIS METHOD, CAUSED BUGS WITH IMPORTS
    root = root.resolve()

    if not root.is_dir():
        raise NotADirectoryError(
            f"Widget discovery root is not a directory: {root}"
        )

    for path in sorted(root.rglob("*.py")):
        if _should_skip(path):
            continue

        module = _load_module(
            root=root,
            path=path,
        )

        _register_widgets(module)

def _load_module(
    *,
    root: Path,
    path: Path,
) -> ModuleType:
    package_name = root.name
    relative = path.relative_to(root)

    if path.name == "__init__.py":
        parts = relative.parent.parts
    else:
        parts = relative.with_suffix("").parts

    module_name = ".".join(
        (package_name, *parts)
    )

    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not create module spec for {path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    return module

def _register_widgets(
    module: ModuleType,
) -> None:
    for name, candidate in inspect.getmembers(
        module,
        inspect.isclass,
    ):
        if candidate.__module__ != module.__name__:
            continue

        if candidate is Widget:
            continue

        if not issubclass(candidate, Widget):
            continue

        if inspect.isabstract(candidate):
            continue

        Factory.register(
            name,
            cls=candidate,
        )

def _should_skip(
    path: Path,
) -> bool:
    return any(
        part == "__pycache__"
        or part.startswith(".")
        for part in path.parts
    )
