from __future__ import annotations

from pathlib import Path

from kivy.core.text import LabelBase
from kivy.event import EventDispatcher
from kivy.properties import StringProperty


class FontManager(EventDispatcher):
    """
    Runtime font registry for kivyfn.

    Responsibilities:
    - Auto-load application fonts
    - Register runtime fonts
    - Expose reactive current font
    - Provide font lookup/introspection

    Note:
    The global default Kivy font is configured by FnConfig.
    """

    current: str = StringProperty(None)

    def __init__(
        self,
        fonts_dir: Path,
        default_font: str,
    ) -> None:
        super().__init__()

        self._loaded = False
        self._registered: set[str] = set()
        self.load(fonts_dir, default_font)


    # =====================================================
    # Public API
    # =====================================================

    def load(self, fonts_dir: Path, default_font: str) -> None:
        """
        Register all .ttf fonts from a directory.

        Safe to call multiple times.
        """
        if self._loaded:
            return

        self._load_fonts(fonts_dir)
        self._loaded = True

        self.current = default_font

    def register(
        self,
        name: str,
        fn_regular: str | Path,
        fn_italic: str | Path | None = None,
        fn_bold: str | Path | None = None,
        fn_bolditalic: str | Path | None = None,
    ) -> None:
        """
        Register a font alias with Kivy.

        Example:
            Label(font_name="MyFont")
        """

        if name in self._registered:
            return

        LabelBase.register(
            name=name,
            fn_regular=str(fn_regular),
            fn_italic=(
                str(fn_italic)
                if fn_italic is not None
                else None
            ),
            fn_bold=(
                str(fn_bold)
                if fn_bold is not None
                else None
            ),
            fn_bolditalic=(
                str(fn_bolditalic)
                if fn_bolditalic is not None
                else None
            ),
        )

        self._registered.add(name)

        if self.current is None:
            self.current = name

    def set(self, name: str) -> None:
        """
        Set the active runtime font alias.
        """

        if not self.has(name):
            raise ValueError(
                f"Font '{name}' is not registered. "
                f"Available: {self.list()}"
            )

        self.current = name

    def has(self, name: str) -> bool:
        """
        Check if a font alias exists.
        """
        return name in self._registered

    def list(self) -> list[str]:
        """
        Return sorted registered font aliases.
        """
        return sorted(self._registered)

    # =====================================================
    # Internal
    # =====================================================

    def _load_fonts(self, fonts_dir: Path) -> None:
        """
        Auto-register all .ttf fonts in a directory.

        Each file becomes:
            FontName.ttf -> "FontName"
        """

        if not fonts_dir.exists():
            return

        for font_file in fonts_dir.glob("*.ttf"):
            self.register(
                name=font_file.stem,
                fn_regular=font_file,
            )

        

    # =====================================================
    # Debug
    # =====================================================

    def __repr__(self) -> str:
        fonts = ", ".join(self.list())

        return (
            f"<FontManager "
            f"current={self.current!r} "
            f"fonts=[{fonts}]>"
        )
