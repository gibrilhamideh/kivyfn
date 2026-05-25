from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(slots=True)
class FnMouseConfig:
    enabled: bool = True
    """
    Enable the Kivy mouse input provider.
    """

    disable_on_activity: bool = False
    """
    Ignore mouse events while another touch provider is active.
    """

    disable_multitouch: bool = True
    """
    Disable right, middle, and ctrl-left multitouch emulation.
    """

    multitouch_on_demand: bool = False
    """
    Only simulate multitouch when explicitly requested.
    """

    disable_hover: bool = False
    """
    Disable mouse hover events.
    """

    def to_kivy(self) -> str:
        if not self.enabled:
            return ""

        tokens = ["mouse"]

        if self.disable_on_activity:
            tokens.append("disable_on_activity")

        if self.disable_multitouch:
            tokens.append("disable_multitouch")

        if self.multitouch_on_demand:
            tokens.append("multitouch_on_demand")

        if self.disable_hover:
            tokens.append("disable_hover")

        return ",".join(tokens)


@dataclass(slots=True)
class FnInputDeviceConfig:
    name: str
    """
    Device configuration name.

    Used as the input configuration key: `device_<name>`.
    """

    enabled: bool = True
    """
    Enable this input device.
    """

    provider: str = "hidinput"
    """
    Kivy input provider name.
    """

    probe: str = "probesysfs"
    """
    Device probe backend.
    """

    max_position_x: int = 32767
    """
    Maximum X coordinate value.
    """

    max_position_y: int = 32767
    """
    Maximum Y coordinate value.
    """

    invert_y: bool = False
    """
    Invert the Y axis input values.
    """

    select_all: bool = True
    """
    Use all matching input devices.
    """

    def key(self) -> str:
        return f"device_{self.name}"

    def to_kivy(self) -> str:
        return (
            f"{self.probe},"
            f"provider={self.provider},"
            f"param=max_position_x={self.max_position_x},"
            f"param=max_position_y={self.max_position_y},"
            f"param=invert_y={int(self.invert_y)},"
            f"select_all={int(self.select_all)}"
        )


@dataclass(slots=True)
class FnInputConfig:
    mouse: FnMouseConfig = field(default_factory=FnMouseConfig)
    """
    Mouse input provider configuration.
    """

    devices: list[FnInputDeviceConfig] = field(default_factory=list)
    """
    Additional input device configurations.

    Useful for touchscreens and custom HID devices.
    """

    def apply(self) -> None:

        from kivy.config import Config
        Config.set("input", "mouse", self.mouse.to_kivy())

        for device in self.devices:
            if not device.enabled:
                continue

            Config.set("input", device.key(), device.to_kivy())
