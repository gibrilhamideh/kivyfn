class FnTouchCapture:
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos): # pyright: ignore
            return super().on_touch_down(touch) # pyright: ignore

        if super().on_touch_down(touch): # pyright: ignore
            return True

        return True

class FnWheelCapture:
    def on_touch_down(self, touch):
        button = getattr(touch, "button", None)
        is_wheel = button in ("scrollup", "scrolldown", "scrollleft", "scrollright")

        if not is_wheel or not self.collide_point(*touch.pos): # pyright: ignore
            return super().on_touch_down(touch) # pyright: ignore

        # let ScrollView / children try first
        for child in self.children[:]: # pyright: ignore
            if child.dispatch("on_touch_down", touch):
                return True

        # child did not use it, block Scene
        return True
