from kivy.uix.gridlayout import GridLayout

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.layouts.adaptive_size import FnLayoutAdaptiveSizeBehavior

class FnGridLayout(
    FnLayoutAdaptiveSizeBehavior,
    FnWidget,
    GridLayout
):
    pass
