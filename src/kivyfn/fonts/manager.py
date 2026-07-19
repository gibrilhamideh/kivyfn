from __future__ import annotations

from pathlib import Path

from kivy.core.text import LabelBase
from kivy.event import EventDispatcher
from kivy.properties import StringProperty


class FontManager(EventDispatcher):
    """
    Runtime font registry for KivyFN.

    Responsibilities:
    - Auto-load application fonts when configured
    - Register framework and application font aliases
    - Expose the reactive current font
    - Provide font lookup and introspection

    The global Kivy default font is configured separately
    through FnFontConfig.
    """

    current: str = StringProperty("NotoSans")

    def __init__(
        self,
        fonts_dir: Path | None = None,
        default_font: str = "NotoSans",
    ) -> None:
        super().__init__()

        self._default_font = default_font
        self._registered: set[str] = set()
        self._loaded_dirs: set[Path] = set()

        self.current = default_font

        if fonts_dir is not None:
            self.load(fonts_dir)

    # =================================== #
    # Loading
    # =================================== #

    def load(
        self,
        fonts_dir: Path,
    ) -> None:
        """
        Register all TTF fonts from a directory.

        Each file is registered using its filename stem:

            Inter-Regular.ttf -> "Inter-Regular"

        Each directory is loaded only once.
        """
        if fonts_dir in self._loaded_dirs:
            return

        if fonts_dir.exists() and not fonts_dir.is_dir():
            raise NotADirectoryError(
                f"Font path is not a directory: {fonts_dir}"
            )

        if fonts_dir.is_dir():
            self._load_fonts(fonts_dir)

        self._loaded_dirs.add(fonts_dir)

    # =================================== #
    # Registration
    # =================================== #

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
        """
        if not isinstance(name, str) or not name:
            raise ValueError(
                "Font name must be a non-empty string"
            )

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

    # =================================== #
    # Current Font
    # =================================== #

    def set(
        self,
        name: str,
    ) -> None:
        """
        Set the active runtime font alias.
        """
        if not self.has(name):
            raise ValueError(
                f"Font {name!r} is not registered. "
                f"Available fonts: {self.list()}"
            )

        self.current = name

    # =================================== #
    # Queries
    # =================================== #

    def has(
        self,
        name: str,
    ) -> bool:
        return (
            name == self._default_font
            or name in self._registered
        )

    def list(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    self._default_font,
                    *self._registered,
                }
            )
        )

    # =================================== #
    # Internal
    # =================================== #

    def _load_fonts(
        self,
        fonts_dir: Path,
    ) -> None:
        for font_file in sorted(
            fonts_dir.glob("*.ttf")
        ):
            self.register(
                name=font_file.stem,
                fn_regular=font_file,
            )

    # =================================== #
    # Debug
    # =================================== #

    def __repr__(self) -> str:
        fonts = ", ".join(self.list())

        return (
            f"<FontManager "
            f"current={self.current!r} "
            f"fonts=[{fonts}]>"
        )
