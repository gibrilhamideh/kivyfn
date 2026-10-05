from __future__ import annotations

from functools import partial

from kivy.graphics import Callback, InstructionGroup, RenderContext
from kivy.graphics.opengl import (
    GL_CURRENT_PROGRAM,
    glGetIntegerv,
    glGetUniformfv,
    glGetUniformLocation,
)

from ..errors import ChartRenderError
from ..geometry import ChartBounds

_VERTEX_SHADER = """
$HEADER$
varying vec2 chart_position;
void main(void) {
    chart_position = vPosition;
    frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
    tex_coord0 = vTexCoords0;
    gl_Position = projection_mat * modelview_mat
        * vec4(vPosition.xy, 0.0, 1.0);
}
"""

_FRAGMENT_SHADER = """
$HEADER$
varying vec2 chart_position;
uniform vec4 chart_bounds;
void main(void) {
    if (chart_position.x < chart_bounds.x
            || chart_position.y < chart_bounds.y
            || chart_position.x > chart_bounds.z
            || chart_position.y > chart_bounds.w) {
        discard;
    }
    gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
}
"""


class PlotClip(InstructionGroup):
    """Clip series fragments in local coordinates before stencil writes."""

    def __init__(self, bounds: ChartBounds) -> None:
        super().__init__()
        self.context = RenderContext(
            use_parent_projection=True, use_parent_modelview=True
        )
        self.context.shader.vs = _VERTEX_SHADER
        self.context.shader.fs = _FRAGMENT_SHADER
        if not self.context.shader.success:
            raise ChartRenderError(
                "Could not compile the plot clipping shader"
            )
        self.context["chart_bounds"] = (
            bounds.left,
            bounds.bottom,
            bounds.right,
            bounds.top,
        )
        self.add(Callback(partial(_inherit_opacity, self.context)))
        self.add(self.context)


def _inherit_opacity(context: RenderContext, _: Callback) -> None:
    # RenderContext inherits matrices but starts its own opacity stack.
    # Read the active parent's scalar uniform at draw time, so ancestor
    # animations and offscreen exports keep their exact canvas opacity.
    program = glGetIntegerv(GL_CURRENT_PROGRAM)[0]
    location = glGetUniformLocation(program, b"opacity") if program else -1
    context.opacity = (
        glGetUniformfv(program, location) if location >= 0 else 1.0
    )
    # glGetUniformfv in Kivy 2.3 accepts only a scalar destination. Never
    # use it for vector uniforms such as color or matrix uniforms.
