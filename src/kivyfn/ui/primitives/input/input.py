from kivy.uix.textinput import TextInput

from ..widget import FnWidget
from ...behaviors.text import FnTextBehavior


class FnInput(FnWidget, FnTextBehavior, TextInput):
    pass
