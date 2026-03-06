"""
Register GabTech widgets to use without import.
"""

from kivy.factory import Factory


def register():
    register = Factory.register

    register("FnBinder", module="kivyfn.ui.binder")
    register("FnRoot", module="kivyfn.ui.root")
    register("FnLabel", module="kivyfn.ui.primitives.label")
    register("FnWidget", module="kivyfn.ui.primitives.widget.base")
