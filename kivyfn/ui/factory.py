"""
Register GabTech widgets to use without import.
"""

from kivy.factory import Factory


def register():
    register = Factory.register

    register("FnRoot", module="kivyfn.ui.root")
    register("FnLabel", module="kivyfn.ui.primitives.label")
