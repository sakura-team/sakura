from sakura.client.opskeleton.tools import join_blocks
from sakura.client.opskeleton.param import generate_param_imports_line, generate_params_declaration
from sakura.client.opskeleton.plug import generate_plugs_declaration
from sakura.client.opskeleton.tab import generate_tabs_declaration

OP_FILE_TEMPLATE = '''\
from sakura.daemon.processing.operator import Operator
%(other_imports)s

%(custom_top_level_code)s

# Operator main class
class %(op_cls_name)s(Operator):
    NAME = "%(op_name)s"
    SHORT_DESC = "bla bla bla operator"   # <- TODO: update this
    TAGS = [ ]                            # <- TODO: update this
    def construct(self):
        %(construct_body)s

    %(custom_methods)s
'''

def generate_operator_py(op_f, skel_info):
    # parameter class imports
    other_imports = [ generate_param_imports_line(skel_info.params) ]
    other_imports.extend((output.custom_imports for output in skel_info.outputs))
    other_imports.extend((tab.custom_imports for tab in skel_info.tabs))
    other_imports = join_blocks(other_imports, '\n', 0)
    # custom top level code
    custom_top_level_code = join_blocks(
        (param.generate_top_level_code() for param in skel_info.params),
        '\n\n', 0)
    # construct method body
    construct_body_lines = []
    construct_body_lines.extend(generate_plugs_declaration(skel_info.inputs))
    construct_body_lines.extend(generate_plugs_declaration(skel_info.outputs))
    construct_body_lines.extend(generate_params_declaration(skel_info.params))
    construct_body_lines.extend(generate_tabs_declaration(skel_info.tabs))
    construct_body = join_blocks(construct_body_lines, '\n', 8)
    # custom code
    custom_mothods_lines = []
    custom_mothods_lines.extend(output.custom_method for output in skel_info.outputs)
    custom_mothods_lines.extend(tab.custom_method for tab in skel_info.tabs)
    custom_methods = join_blocks(custom_mothods_lines, '\n\n', 4)
    # format according to general file template
    print(OP_FILE_TEMPLATE % dict(
        op_name = skel_info.op_name,
        op_cls_name = skel_info.op_cls_name,
        other_imports = other_imports,
        custom_top_level_code = custom_top_level_code,
        construct_body = construct_body,
        custom_methods = custom_methods
    ), file=op_f)
