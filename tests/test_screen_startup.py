"""Screen startup progress must leave frames for the UI to draw."""

import unittest

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import NoTransition

from kivyfn.ui.navigation.screen import (
    FnScreen,
    FnScreenManager,
    FnSplashScreen,
)


class StartupScreen(FnScreen):
    def __init__(self, *, builds, automatic=True, **kwargs):
        self.builds = builds
        self.automatic = automatic
        super().__init__(**kwargs)

    def build(self):
        self.builds.append((self.name, Clock.frames))
        if self.automatic:
            self.ready()


class ScreenStartupTests(unittest.TestCase):
    def tick(self, count=1):
        for _ in range(count):
            Clock.tick()
            Clock.tick_draw()

    def finish(self, manager):
        for _ in range(30):
            if manager.loaded:
                break
            self.tick()
        self.assertTrue(manager.loaded)

    def test_progress_is_visible_between_screen_builds(self):
        builds = []
        splash = FnSplashScreen(name="splash")
        manager = FnScreenManager(transition=NoTransition())
        manager.add_widget(splash)
        for name in ("first", "second", "third"):
            manager.add_widget(StartupScreen(name=name, builds=builds))

        progress = []
        splash.bind(loaded=lambda _, value: progress.append(value))
        manager.start()
        self.assertEqual(builds, [])
        self.assertEqual(splash.total, 3)
        self.assertEqual(splash.progress, 0)
        self.assertEqual(manager.current, "splash")

        self.tick()
        self.assertEqual(splash.current_screen, "first")
        self.assertEqual(builds, [])
        self.tick()
        self.assertEqual(splash.loaded, 1)
        self.assertEqual(len(builds), 1)
        self.assertEqual(manager.current, "splash")

        self.finish(manager)
        self.assertEqual(progress, [1, 2, 3])
        self.assertEqual(splash.progress, 1)
        self.assertEqual(manager.current, "first")
        self.assertFalse(manager.loading)
        frames = [frame for _, frame in builds]
        self.assertTrue(all(b > a for a, b in zip(frames, frames[1:])))

        # Cleanup must not reset a completed external progress display.
        self.tick(10)
        self.assertEqual(splash.current_screen, "third")
        self.assertEqual(splash.progress, 1)

    def test_external_splash_waits_for_asynchronous_readiness(self):
        builds = []
        splash = FnSplashScreen()
        manager = FnScreenManager(
            splash_screen=splash, transition=NoTransition()
        )
        slow = StartupScreen(name="slow", builds=builds, automatic=False)
        manager.add_widget(slow)
        manager.add_widget(StartupScreen(name="next", builds=builds))
        manager.start()
        self.tick(5)
        self.assertEqual([name for name, _ in builds], ["slow"])
        self.assertEqual(splash.loaded, 0)
        self.assertTrue(manager.loading)

        slow.ready()
        self.assertEqual(splash.loaded, 1)
        self.assertEqual(len(builds), 1)
        self.finish(manager)
        self.assertEqual(splash.loaded, 2)
        self.assertIsNone(splash.parent)

    def test_lazy_target_and_prebuilt_screens_are_counted_once(self):
        builds = []
        manager = FnScreenManager(
            initial_screen="target", transition=NoTransition()
        )
        prepared = StartupScreen(name="prepared", builds=builds)
        target = StartupScreen(name="target", load="lazy", builds=builds)
        deferred = StartupScreen(
            name="deferred", load="lazy", builds=builds
        )
        for screen in (prepared, target, deferred):
            manager.add_widget(screen)
        prepared._build()
        manager.start()
        self.finish(manager)
        self.assertEqual([name for name, _ in builds], ["prepared", "target"])
        self.assertFalse(deferred.built)
        self.assertEqual(manager.current, "target")
        with self.assertRaises(RuntimeError):
            manager.start()

    def test_factories_wait_for_the_previous_screen(self):
        builds = []
        created = []
        splash = FnSplashScreen()
        manager = FnScreenManager(splash_screen=splash)

        def factory(name, automatic):
            self.assertEqual(splash.current_screen, name)
            created.append(name)
            return StartupScreen(
                name=name, builds=builds, automatic=automatic
            )

        manager.register_screen("first", lambda: factory("first", False))
        manager.register_screen("second", lambda: factory("second", True))
        self.assertEqual(manager.screens, [])
        manager.start()
        self.assertEqual(created, [])
        self.tick(5)
        self.assertEqual(created, ["first"])
        self.assertEqual(splash.loaded, 0)
        manager.get_screen("first").ready()
        self.finish(manager)
        self.assertEqual(created, ["first", "second"])
        self.assertEqual(splash.loaded, 2)

    def test_kv_assigns_child_names_after_widgets_are_added(self):
        class DeclaredStartupScreen(FnScreen):
            def build(self):
                self.ready()

        manager = Builder.load_string('''
FnScreenManager:
    DeclaredStartupScreen:
        name: "first"
    DeclaredStartupScreen:
        name: "second"
''')
        manager.start()
        self.finish(manager)
        self.assertEqual(manager._startup_total, 2)
        self.assertTrue(manager.get_screen("first").is_ready)
        self.assertTrue(manager.get_screen("second").is_ready)

    def test_factory_failure_stops_without_false_progress(self):
        manager = FnScreenManager(splash_screen=FnSplashScreen())
        failures = []
        calls = []

        def broken():
            raise ValueError("Cannot construct screen")

        manager.register_screen("broken", broken)
        manager.register_screen("later", lambda: calls.append(True))
        manager.bind(on_startup_failed=lambda _, error: failures.append(error))
        manager.start()
        self.tick(5)
        self.assertFalse(manager.loading)
        self.assertFalse(manager.loaded)
        self.assertEqual(manager.splash_screen.loaded, 0)
        self.assertEqual(manager.splash_screen.current_screen, "broken")
        self.assertEqual(str(failures[0]), "Cannot construct screen")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
