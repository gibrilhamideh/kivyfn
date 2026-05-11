"""
Register FnKivy-ui widgets to use without import.
"""

from kivy.base import Builder

def register():

    Builder.load_string(
        """
        #: import Animation kivy.animation.Animation
        #: import RelativeLayout kivy.uix.relativelayout.RelativeLayout
        #: import Factory kivy.factory.Factory
        #: import tr kivyfn.i18n.i18n


    """
    )
