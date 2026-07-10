# recycleview/boxlayout.py

from kivy.uix.recycleboxlayout import RecycleBoxLayout

from kivyfn.ui.behaviors.layouts.adaptive_size import (
    FnLayoutAdaptiveSizeBehavior,
)


class FnRecycleBoxLayout(
    FnLayoutAdaptiveSizeBehavior,
    RecycleBoxLayout,
):
    pass
