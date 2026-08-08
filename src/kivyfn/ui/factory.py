"""
Register FnKivy-ui widgets to use without import.
"""

from kivy.factory import Factory
from kivy.base import Builder
from kivyfn.ui.paths import UI_BEHAVIOR_PATH


def register():
    register = Factory.register

    # ---) Base Widget
    register("FnWidget", module="kivyfn.ui.widget")
    register("FnRoot", module="kivyfn.ui.root")

    # ---) Navigation
    register("FnScreenManager", module="kivyfn.ui.navigation.screens")
    register("FnScreen", module="kivyfn.ui.navigation.screens")
    register("FnSplashScreen", module="kivyfn.ui.navigation.screens")

    # ---) Primitive Layout
    register("FnBoxLayout", module="kivyfn.ui.layouts.boxlayout")
    register("FnGridLayout", module="kivyfn.ui.layouts.gridlayout")
    register("FnFloatLayout", module="kivyfn.ui.layouts.floatlayout")
    register("FnRelativeLayout", module="kivyfn.ui.layouts.relativelayout")
    register("FnScrollView", module="kivyfn.ui.layouts.scrollview")

    # ---) Layout
    register("FnBoxLayout", module="kivyfn.ui.layouts.boxlayout")
    register("FnFloatLayout", module="kivyfn.ui.layouts.floatlayout")
    register("FnGridLayout", module="kivyfn.ui.layouts.gridlayout")
    register("FnRelativeLayout", module="kivyfn.ui.layouts.relativelayout")
    register("FnScrollView", module="kivyfn.ui.layouts.scrollview")
    register("FnBlurLayout", module="kivyfn.ui.layouts.blurlayout")

    # ---) Recycle View
    register("FnRecycleView", module="kivyfn.ui.collections.recycleview")
    register("FnRecycleBoxlayout", module="kivyfn.ui.collections.recycleview")
    register("FnRecycleGridLayout", module="kivyfn.ui.collections.recycleview")

    # ---) Fields
    register("FnCompositeField", module="kivyfn.ui.fields.compostie")
    register("FnMaskField", module="kivyfn.ui.fields.mask")
    register("FnNumericField", module="kivyfn.ui.fields.numeric")


    # ---) Images
    register("FnImage", module="kivyfn.ui.image")


    # ========================================= #
    # Kivy Lang files 
    # ========================================= #

    # ---) transform behaviors
    Builder.load_file(str(UI_BEHAVIOR_PATH / "canvas" / "override" / "override.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "canvas" / "clip" / "clip.kv"))

    # ---) transform behaviors
    Builder.load_file(str(UI_BEHAVIOR_PATH / "transform" / "scale" / "scale.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "transform" / "rotate" / "rotate.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "transform" / "translate" / "translate.kv"))

    # ---) style behaviors
    Builder.load_file(str(UI_BEHAVIOR_PATH / "style" / "elevation" / "elevation.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "style" / "background" / "background.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "style" / "border" / "border.kv"))

    # ---> field behaviors
    Builder.load_file(str(UI_BEHAVIOR_PATH / "field" / "border" / "border.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "field" / "layout" / "layout.kv"))
    Builder.load_file(str(UI_BEHAVIOR_PATH / "field" / "text" / "text.kv"))


