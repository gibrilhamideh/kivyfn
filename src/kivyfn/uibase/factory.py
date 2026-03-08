"""
Register FnKivy widgets to use without import.
"""

from kivy.factory import Factory


def register():
    register = Factory.register

    # ---) Context
    register("FnBinder", module="kivyfn.uibase.binder")

    # ---) Primitives
    register("FnWidget", module="kivyfn.uibase.primitives.widget.base")
    register("FnRoot", module="kivyfn.uibase.root")
    register("FnLabel", module="kivyfn.uibase.primitives.label")

    # ---) Navigation
    register("FnScreenManager", module="kivyfn.uibase.navigation")
    register("FnScreen", module="kivyfn.uibase.navigation")
    register("FnSplashScreen", module="kivyfn.uibase.navigation")
