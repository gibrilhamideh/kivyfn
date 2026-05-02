from __future__ import annotations


from kivy.core.text import LabelBase
from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from kivyfn.resources import framework_resource


class FontManager(EventDispatcher):
    """
    Minimal typography system for kivyfn.

    Responsibilities:
    - Register framework default font
    - Register framework icon font
    - Register optional app fonts
    - Expose reactive `current` font
    - Provide introspection utilities for debugging
    """

    current = StringProperty("FnDefault")

    _default_name = "FnDefault"
    _icons_name = "FnIcons"

    def __init__(self) -> None:
        super().__init__()
        self._loaded = False
        self._registered: set[str] = set()

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def load(self, path) -> None:
        """
        Load framework + app fonts.
        Safe to call multiple times.
        """
        if self._loaded:
            return

        self._load_framework_fonts()
        self._load_app_fonts(path)

        self._loaded = True

    def list(self) -> list[str]:
        """
        Return sorted list of available font names.
        """
        return sorted(self._registered)

    def has(self, name: str) -> bool:
        """
        Check if font is registered.
        """
        return name in self._registered

    def default(self) -> str:
        return self._default_name

    def icons(self) -> str:
        return self._icons_name

    def set(self, name: str) -> None:
        """
        Set current font safely.
        """
        if not self.has(name):
            raise ValueError(
                f"Font '{name}' is not registered. Available: {self.list()}"
            )

        self.current = name

    def __repr__(self) -> str:
        fonts = ", ".join(self.list())
        return f"<FontManager current='{self.current}' fonts=[{fonts}]>"

    # -----------------------------------------------------
    # Internal
    # -----------------------------------------------------

    def _register(
        self,
        name: str,
        fn_regular: str,
        fn_bold: str | None = None,
    ) -> None:
        """
        Internal safe registration wrapper.
        Prevents duplicate tracking.
        """
        if name in self._registered:
            return

        if fn_bold:
            LabelBase.register(
                name=name,
                fn_regular=fn_regular,
                fn_bold=fn_bold,
            )
        else:
            LabelBase.register(
                name=name,
                fn_regular=fn_regular,
            )

        self._registered.add(name)

    def _load_framework_fonts(self) -> None:
        fonts_dir = framework_resource("kivyfn", "resources", "fonts")

        # --- Default UI font
        self._register(
            name=self._default_name,
            fn_regular=str(fonts_dir / "NotoSans-Regular.ttf"),
            fn_bold=str(fonts_dir / "NotoSans-Bold.ttf"),
        )

        # --- Icon font
        icons_path = fonts_dir / "Material-Design-Icons.ttf"
        if icons_path.exists():
            self._register(
                name=self._icons_name,
                fn_regular=str(icons_path),
            )

    def _load_app_fonts(self, fonts_dir) -> None:
        """
        Register fonts from app/fonts directory.
        Each .ttf becomes available by its file stem.
        """

        if not fonts_dir.exists():
            return

        for font_file in fonts_dir.glob("*.ttf"):
            self._register(
                name=font_file.stem,
                fn_regular=str(font_file),
            )
