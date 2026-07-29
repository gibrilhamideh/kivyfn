# kivyfn/config/base.py
from __future__ import annotations
from pathlib import Path

from kivyfn.config.environment import FnEnvironmentConfig
from kivyfn.config.fonts import FnFontConfig
from kivyfn.config.graphics import FnGraphicsConfig
from kivyfn.config.input import FnInputConfig
from kivyfn.config.keyboard import FnKeyboardConfig
from kivyfn.config.logging import FnLoggingConfig
from kivyfn.config.widgets import FnWidgetsConfig

class FnConfig:
    """
    Base configuration class for KivyFn applications.
    
    This class handles the resolution of application paths and orchestrates 
    the application of various sub-configs (fonts, input, graphics, etc.).
    """

    environment: FnEnvironmentConfig = FnEnvironmentConfig()
    """Controls environment variables."""

    fonts: FnFontConfig = FnFontConfig()
    """Controls application font registration and defaults."""

    graphics: FnGraphicsConfig = FnGraphicsConfig()
    """Controls window size, fullscreen behavior, and graphics settings."""

    input: FnInputConfig = FnInputConfig()
    """Controls mouse, touch, and other input behavior."""

    keyboard: FnKeyboardConfig = FnKeyboardConfig()
    """Controls keyboard shortcuts and keyboard behavior."""

    logging: FnLoggingConfig = FnLoggingConfig()
    """Controls application logging behavior and log output."""

    widgets: FnWidgetsConfig = FnWidgetsConfig()
    """Provides global defaults for widget behavior and styling."""

    resources_dir: Path
    """Application resources directory. Defaults to `app_dir/resources`."""

    locales_dir: Path
    """Translation and localization files directory. Defaults to `resources_dir/locales`."""

    fonts_dir: Path
    """Application fonts directory. Defaults to `resources_dir/fonts`."""

    settings_path: Path
    """Application settings file path. Defaults to `app_dir/settings.json`."""

    def __init__(self, app_dir: Path) -> None:
        """
        Initializes the configuration and resolves internal paths.
        
        Args:
            app_dir: Root application directory used as the base for path resolution.
        """
        self.app_dir = app_dir
        """Root application directory."""

        # -----------------------------------------------------
        # Resources Resolution
        # -----------------------------------------------------
        if not hasattr(self, "resources_dir"):
            self.resources_dir = self.app_dir / "resources"

        # -----------------------------------------------------
        # Locales Resolution
        # -----------------------------------------------------
        if not hasattr(self, "locales_dir"):
            self.locales_dir = self.resources_dir / "locales"

        # -----------------------------------------------------
        # Fonts Resolution
        # -----------------------------------------------------
        if not hasattr(self, "fonts_dir"):
            self.fonts_dir = self.resources_dir / "fonts"

        # -----------------------------------------------------
        # Settings Resolution
        # -----------------------------------------------------
        if not hasattr(self, "settings_path"):
            self.settings_path = self.app_dir / "settings.json"

        # -----------------------------------------------------
        # Apply Kivy Config
        # -----------------------------------------------------
        self.apply()

    def apply(self) -> None:
        """Triggers the .apply() method on all sub-configuration objects."""
        self.environment.apply()
        self.logging.apply()
        self.fonts.apply()
        self.graphics.apply()
        self.input.apply()
        self.keyboard.apply()
        self.widgets.apply()


