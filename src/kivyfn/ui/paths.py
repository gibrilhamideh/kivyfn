# kivyfn/ui/paths.py

from kivyfn.paths import package_path


UI_PACKAGE_PATH = package_path("kivyfn.ui")

UI_RESOURCE_PATH = package_path(
    "kivyfn.ui",
    "resources",
)

UI_BEHAVIOR_PATH = package_path(
    "kivyfn.ui",
    "behaviors",
)

UI_FONT_PATH = UI_RESOURCE_PATH / "fonts"
UI_ICON_PATH = UI_RESOURCE_PATH / "icons"
UI_KV_PATH = UI_RESOURCE_PATH / "kv"
