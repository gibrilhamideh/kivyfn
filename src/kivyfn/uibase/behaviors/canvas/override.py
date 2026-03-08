from kivy.lang import Builder

Builder.load_string(
    """
<FnCanvasOverrideBehavior>
    canvas.before:
        Clear
"""
)


class FnCanvasOverrideBehavior:
    pass
