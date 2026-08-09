from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

from kivyfn.paths import package_path


@dataclass(slots=True)
class FnFontConfig:
    name: str = "NotoSans"
    """
    Global default font alias used by Kivy widgets.
    """

    regular_path: Path = package_path(
        "kivyfn",
        "ui",
        "resources",
        "fonts",
        "text",
        "NotoSans-Regular.ttf",
    )
    """
    Regular font file path.
    """

    italic_path: Path = package_path(
        "kivyfn",
        "ui",
        "resources",
        "fonts",
        "text",
        "NotoSans-Italic.ttf",
    )
    """
    Italic font file path.
    """

    bold_path: Path = package_path(
        "kivyfn",
        "ui",
        "resources",
        "fonts",
        "text",
        "NotoSans-Bold.ttf",
    )
    """
    Bold font file path.
    """

    bold_italic_path: Path = package_path(
        "kivyfn",
        "ui",
        "resources",
        "fonts",
        "text",
        "NotoSans-BoldItalic.ttf",
    )
    """
    Bold italic font file path.
    """

    def apply(self) -> None:

        from kivy.config import Config
        Config.set(
            "kivy",
            "default_font",
            [
                self.name,
                str(self.regular_path),
                str(self.italic_path),
                str(self.bold_path),
                str(self.bold_italic_path),
            ],
        )

