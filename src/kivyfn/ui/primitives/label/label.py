from kivy.base import Builder
from kivy.uix.label import Label

from ..widget import FnWidget
from ...behaviors.text import FnTextBehavior

from ....resources import framework_resource

kv_path = framework_resource("ui", "primitives", "label", "label.kv")
Builder.load_file(str(kv_path))


class FnLabel(FnWidget, FnTextBehavior, Label):
    pass
