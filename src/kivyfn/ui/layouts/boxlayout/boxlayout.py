from kivy.uix.boxlayout import BoxLayout

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.layouts.adaptive_size import FnLayoutAdaptiveSizeBehavior

class FnBoxLayout(
    FnLayoutAdaptiveSizeBehavior,
    FnWidget,
    BoxLayout
):
    pass
