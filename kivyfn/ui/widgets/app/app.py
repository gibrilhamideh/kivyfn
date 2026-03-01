from __future__ import annotations

import os

from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty

from theme import Theme
from lib.translate import Translate
from paths import resources_path


class FnApp(App):
    language = StringProperty("english")
    """
    `language` the current language of the application

    :attr:`language` is a :class:`~kivy.Properties.StringProperty`
    """

    theme: Theme = ObjectProperty()
    """
    `theme` is the current theme of the application

    :attr:`theme` is a :class:`~kivy.Properties.ObjectProperty`
    """

    translate: Translate = ObjectProperty(Translate())
    """
    `translate` is the translation instance

    :attr:`translate` is a :class:`~kivy.Properties.ObjectProperty`
    """

    components = ObjectProperty()
    """
    `components` is a reference to all the components in the application

    :attr:`components` is a :class:`~kivy.Properties.ObjectProperty`
    """

    resource_path: str = StringProperty(resources_path)
    """
    `resource_path` is the path to the resources folder

    :attr:`resource_path` is a :class:`~kivy.Properties.StringProperty`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_init()
        self.root: KcNavigation

    def on_start(self):
        self.on_preload()
        self.root.bind(on_complete=lambda *_: self.on_postload())
        self.root.start()

    # ==================================================== #
    # Events
    # ==================================================== #
    def on_init(self):
        pass

    def on_exit(self):
        pass

    def on_preload(self):
        pass

    def on_postload(self):
        pass

    # ==================================================== #
    # Utility methods
    # ==================================================== #
    def get_resource_path(self, resource, file) -> str:
        return os.path.join(self.resource_path, resource, file)
