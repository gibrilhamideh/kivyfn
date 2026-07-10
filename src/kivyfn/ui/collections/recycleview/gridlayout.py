# recycleview/gridlayout.py

from kivy.uix.recyclegridlayout import RecycleGridLayout

from kivyfn.ui.behaviors.layouts.adaptive_size import (
    FnLayoutAdaptiveSizeBehavior,
)

class FnRecycleGridLayout(
    FnLayoutAdaptiveSizeBehavior,
    RecycleGridLayout,
):
    pass
