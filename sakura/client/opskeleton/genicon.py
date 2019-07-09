#!/usr/bin/env python
import random, math

SVG_HEADER = """<svg height="38" width="38">"""
SVG_FOOTER = """</svg>"""

CIRCLE_PATTERN="""\
<circle r="%(r)d" stroke="#000" cx="%(cx)f" cy="%(cy)f" stroke-width="%(sw)f" fill="%(fill_color)s"/> \
"""

def circle(f, r, cx, cy, stroke_width):
    fill_color = 0
    for i in range(3):
        fill_color *= 16
        fill_color += random.randrange(16)
    fill_color = '#' + hex(fill_color)[2:].zfill(3)
    print(CIRCLE_PATTERN % dict(
        r = r,
        cx = cx,
        cy = cy,
        sw = stroke_width,
        fill_color = fill_color
    ), file=f)

def generate_random_icon(f):
    print(SVG_HEADER, file=f)
    circle(f, 17, 19, 19, 2)
    for i in range(6):
        r = random.randrange(3, 10)
        center_d = 17 - r
        center_x = random.uniform(-center_d, center_d)
        center_y = random.choice((-1, 1)) * math.sqrt((center_d * center_d) - (center_x * center_x))
        center_x += 19
        center_y += 19
        circle(f, r, center_x, center_y, 0.5)
    print(SVG_FOOTER, file=f)
