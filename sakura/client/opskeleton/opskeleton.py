#!/usr/bin/env python3
import sys, pathlib
from sakura.client.opskeleton.tools import ask_int, ask_val_of_set, ask_camel_case_name
from sakura.client.opskeleton.param import PARAM_CLASSES
from sakura.client.opskeleton.genicon import generate_random_icon
from sakura.client.opskeleton.genoperator import generate_operator_py
from sakura.client.opskeleton.analyse import SkeletonInfo

USAGE = "Usage: %s <directory>" % sys.argv[0]

def run():
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    opdir = pathlib.Path(sys.argv[1])
    if opdir.exists():
        if not opdir.is_dir():
            sys.exit('Sorry, %s already exists and is not a directory. Giving up.' % sys.argv[1])
        if len(tuple(opdir.glob('*'))) > 0:
            sys.exit('Sorry, directory %s already exists and is not empty. Giving up.' % sys.argv[1])
    op_name = ask_camel_case_name('How would you like to name this operator?', 15)
    num_inputs = ask_int('How many inputs should this operator class accept?', 0, 5)
    num_outputs = ask_int('How many outputs should this operator class have?', 0, 5)
    num_parameters = ask_int('How many parameters should this operator class have?', 0, 5)
    if num_inputs > 0:
        param_cls_filter = lambda cls: True  # no filter
    else:
        param_cls_filter = lambda cls: not cls.needs_one_input()
    param_classes_desc = { str(cls_id+1): cls.__doc__ \
            for cls_id, cls in enumerate(PARAM_CLASSES)
                if param_cls_filter(cls) }
    param_classes = []
    for param_id in range(1, 1+num_parameters):
        param_cls_id = int(ask_val_of_set('What kind of parameter is parameter %d?' % param_id, param_classes_desc)) -1
        param_cls = PARAM_CLASSES[param_cls_id]
        param_classes.append(param_cls)
    num_tabs = ask_int('How many custom html tabs will your operator provide?', 0, 5)
    # OK, let's start working
    skel_info = SkeletonInfo(op_name, num_inputs, num_outputs, param_classes, num_tabs)
    if not opdir.exists():
        opdir.mkdir(parents=True)
    with (opdir / 'icon.svg').open('w') as icon_f:
        generate_random_icon(icon_f)
    with (opdir / 'operator.py').open('w') as op_f:
        generate_operator_py(op_f, skel_info)
    for tab in skel_info.tabs:
        tab.generate_files(opdir)
    print('Operator class skeleton was generated in directory: ' + sys.argv[1])

if __name__ == '__main__':
    run()
