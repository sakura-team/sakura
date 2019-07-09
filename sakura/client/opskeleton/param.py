from collections import defaultdict

CUSTOM_COMBO_CODE = '''\
# Sample code for a custom combo parameter
class %(cls_name)s(ComboParameter):
    VALUES = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
               'Saturday', 'Sunday' ]
    def get_possible_items(self):
        # This method must return a list of tuples.
        # Each tuple should have the form: (<integer-id>, <string-label>).
        # The GUI will use <string-label> for displaying the combo items.
        # When the user selects an item, the 'value' attribute of this
        # combo parameter (i.e. self.value) will be set to the associated
        # <integer-id>.
        return list(enumerate(%(cls_name)s.VALUES))
'''

class Param:
    def __init__(self, param_name, inputs):
        self.name = param_name
        self.label = param_name.replace('_', ' ').capitalize()
    @property
    def decl_pattern(self):
        return PARAM_DESCR_TEMPLATE % dict(
            param_name = self.name,
            cls_name = self.cls_name,
            constructor_args = self.generate_constructor_args_string()
        )
    @property
    def cls_name(self):
        return self.__class__.__name__
    def get_cls_imports(self):
        return self.cls_name
    def generate_top_level_code(self):
        return ''

class ColumnSelectionParam(Param):
    def __init__(self, param_name, inputs):
        Param.__init__(self, param_name, inputs)
        self.linked_input = next(inputs)
    def generate_constructor_args_string(self):
        return "'%(param_label)s', self.%(input_name)s" % dict(
                param_label = self.label,
                input_name = self.linked_input.name
        )

class TagBasedColumnSelection(ColumnSelectionParam):
    'tag-based input column selection (combobox)'
    def generate_constructor_args_string(self):
        return ColumnSelectionParam.generate_constructor_args_string(self) + ", 'my-tag'"

class NumericColumnSelection(ColumnSelectionParam):
    'numeric input column selection (combobox)'

class StrColumnSelection(ColumnSelectionParam):
    'text (string) input column selection (combobox)'

class FloatColumnSelection(ColumnSelectionParam):
    'float input column selection (combobox)'

class ComboParameter(Param):
    'other kind of combobox'
    NEXT_COMBO_NUM = 1
    def __init__(self, param_name, inputs):
        Param.__init__(self, param_name, inputs)
        self.num = ComboParameter.NEXT_COMBO_NUM
        ComboParameter.NEXT_COMBO_NUM += 1
    def generate_constructor_args_string(self):
        return "'%s'" % self.label
    @property
    def cls_name(self):
        return 'CustomCombo' + str(self.num)
    def generate_top_level_code(self):
        return CUSTOM_COMBO_CODE % dict(cls_name = self.cls_name)
    def get_cls_imports(self):
        return 'ComboParameter' # this will be our base class

PARAM_CLASSES = [
    TagBasedColumnSelection,
    NumericColumnSelection,
    StrColumnSelection,
    FloatColumnSelection,
    ComboParameter
]

PARAM_IMPORT_TEMPLATE = '''\
from sakura.daemon.processing.parameter import %(cls_names)s\
'''

def generate_param_imports_line(params):
    if len(params) == 0:
        return ''
    cls_names = set(param.get_cls_imports() for param in params)
    return PARAM_IMPORT_TEMPLATE % dict(
        cls_names = ', '.join(cls_names)
    )

PARAM_DESCR_TEMPLATE = '''\
self.%(param_name)s = self.register_parameter(
        %(cls_name)s(%(constructor_args)s))\
'''

def get_param_name_prefix(param_cls):
    if 'ColumnSelection' in param_cls.__name__:
        return 'column_param'
    else:
        return 'param'

# if several parameters are refering to an input, then
# they probably refer each one to a different input.
def iterate_inputs(inputs):
    while True:
        yield from inputs

def generate_params(param_classes, inputs):
    inputs = iterate_inputs(inputs)
    # select a meaningful name prefix for each parameter
    prefixes = defaultdict(list)
    for param_id, cls in enumerate(param_classes):
        prefix = get_param_name_prefix(cls)
        prefixes[prefix].append(param_id)
    # if several params have the same prefix, add a numeric suffix
    param_names = {}
    for prefix, param_ids in prefixes.items():
        if len(param_ids) == 1:
            param_names[param_ids[0]] = prefix
        else:
            for suffix_num, param_id in enumerate(param_ids):
                param_names[param_id] = prefix + '_' + str(suffix_num+1)
    # generate description
    params = []
    for param_id, cls in enumerate(param_classes):
        param_name = param_names[param_id]
        params.append(cls(param_name, inputs))
    return params

def generate_params_declaration(params):
    if len(params) == 0:
        return []
    lines = [ "# parameters" ]
    lines.extend(p.decl_pattern for p in params)
    return lines
