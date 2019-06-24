#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from sakura.common.gpu.openglapp import OpenglApp
from stc.spacetimecube import SpaceTimeCube
from sakura.common.gpu.openglapp import MouseMoveReporting

if len(sys.argv) < 2:
    print("\33[1;31mERROR !! We need a csv file\33[m")
    sys.exit()

current_dir = Path(__file__).parent
oapp = OpenglApp(SpaceTimeCube(current_dir))
oapp.handler.debug = True

if '-shape' in sys.argv:
    ind = sys.argv.index('-shape')
    oapp.handler.set_floor_shape_file(sys.argv[ind+1])

oapp.init(800, 600)
oapp.plan_periodic_task(oapp.handler.animation, .01)
#oapp.mouse_move_reporting = getattr(oapp.handler,
#                                    "mouse_move_reporting",
#                                    MouseMoveReporting.ALWAYS)
oapp.handler.clean_data()
if '-c' in sys.argv:
    ind = sys.argv.index('-c')
    oapp.handler.set_colors_file(sys.argv[ind+1])

oapp.handler.load_data(file=sys.argv[1])
oapp.handler.update_floor()
oapp.loop()
