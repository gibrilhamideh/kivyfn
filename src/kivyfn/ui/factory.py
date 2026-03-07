"""
Register FnKivy widgets to use without import.
"""

from kivy.factory import Factory


def register():
    register = Factory.register

    # ---) Context
    register("FnBinder", module="kivyfn.ui.binder")

    # ---) Primitives
    register("FnWidget", module="kivyfn.ui.primitives.widget.base")
    register("FnRoot", module="kivyfn.ui.root")
    register("FnLabel", module="kivyfn.ui.primitives.label")

    # ---) Navigation
    register("FnScreenManager", module="kivyfn.ui.navigation")
    register("FnScreen", module="kivyfn.ui.navigation")
    register("FnSplashScreen", module="kivyfn.ui.navigation")
