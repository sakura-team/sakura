from sakura.client.opskeleton.tools import join_blocks
from sakura.client.opskeleton.param import generate_param_import_lines, generate_params_declaration
from sakura.client.opskeleton.plug import generate_plugs_declaration
from sakura.client.opskeleton.tab import generate_tabs_declaration

OP_FILE_TEMPLATE = '''\
%(imports)s

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
    # imports
    imports = ('from sakura.daemon.processing.operator import Operator',)
    imports += generate_param_import_lines(skel_info.params)
    for output in skel_info.outputs:
        imports += output.custom_imports
    for tab in skel_info.tabs:
        imports += tab.custom_imports
    imports = sorted(set(imports))  # sort and make unique
    imports = join_blocks(imports, '\n', 0)
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
    custom_methods_lines = []
    custom_methods_lines.extend(param.custom_method for param in skel_info.params)
    custom_methods_lines.extend(output.custom_method for output in skel_info.outputs)
    custom_methods_lines.extend(tab.custom_method for tab in skel_info.tabs)
    custom_methods = join_blocks(custom_methods_lines, '\n\n', 4)
    # format according to general file template
    print(OP_FILE_TEMPLATE % dict(
        op_name = skel_info.op_name,
        op_cls_name = skel_info.op_cls_name,
        imports = imports,
        custom_top_level_code = custom_top_level_code,
        construct_body = construct_body,
        custom_methods = custom_methods
    ), file=op_f)
