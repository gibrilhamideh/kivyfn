from __future__ import annotations

from kivy.graphics.texture import Texture

# A reusable lookup of distance/line-height makes the fade follow sloping
# segments without the diagonal seams of ordinary per-vertex alpha. Keeping
# the default Kivy shader also preserves every ancestor canvas's opacity.
GRADIENT_SIZE = 256
_texture: Texture | None = None
_pixels: bytes | None = None


def gradient_texture() -> Texture:
    """Return the shared, reloadable area-gradient lookup texture."""
    global _texture
    if _texture is None:
        texture = Texture.create(
            size=(GRADIENT_SIZE, GRADIENT_SIZE), colorfmt="rgba"
        )
        texture.min_filter = "linear"
        texture.mag_filter = "linear"
        texture.wrap = "clamp_to_edge"
        _reload_texture(texture)
        texture.add_reload_observer(_reload_texture)
        _texture = texture

    return _texture


def _reload_texture(texture: Texture) -> None:
    global _pixels
    if _pixels is None:
        pixels = bytearray(b"\xff\xff\xff\x00" * GRADIENT_SIZE**2)
        for distance in range(1, GRADIENT_SIZE):
            for height in range(GRADIENT_SIZE):
                alpha = 1.0 if height <= distance else distance / height
                offset = (distance * GRADIENT_SIZE + height) * 4 + 3
                pixels[offset] = round(alpha * 255)

        _pixels = bytes(pixels)

    texture.blit_buffer(_pixels, colorfmt="rgba", bufferfmt="ubyte")
