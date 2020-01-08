from collections import defaultdict

PARAM_REGISTERING_TEMPLATE = '''\
self.%(param_name)s = self.register_parameter(
%(register_parameter_args)s)\
'''

PARAM_TYPE_ARG = "'%(type_name)s'"
PARAM_LABEL_ARG = "label='%(label)s'"

class Param:
    def __init__(self, type_name, param_name, inputs):
        self.type_name = type_name
        self.name = param_name
        self.label = param_name.replace('_', ' ').capitalize()
    @property
    def decl_pattern(self):
        args = self.generate_register_parameter_args()
        formatted_args = ',\n'.join((' '*8 + arg) for arg in args)
        return PARAM_REGISTERING_TEMPLATE % dict(
            param_name = self.name,
            register_parameter_args = formatted_args
        )
    def generate_register_parameter_args(self):
        return [
            PARAM_TYPE_ARG % dict(type_name = self.type_name),
            PARAM_LABEL_ARG % dict(label = self.label)
        ]
    def get_imports(self):
        return ()
    def generate_top_level_code(self):
        return ''
    @property
    def custom_method(self):
        return ''

class ColumnSelectionParam(Param):
    def __init__(self, type_name, param_name, inputs):
        Param.__init__(self, type_name, param_name, inputs)
        self.linked_input = next(inputs)
    def generate_register_parameter_args(self):
        return Param.generate_register_parameter_args(self) + [
            "plug=self.%(input_name)s" % dict(input_name = self.linked_input.name)
        ]
    @classmethod
    def needs_one_input(cls):
        return True

class TagBasedColumnSelection(ColumnSelectionParam):
    'tag-based input column selection (combobox)'
    def __init__(self, param_name, inputs):
        ColumnSelectionParam.__init__(self, 'TAG_BASED_COLUMN_SELECTION', param_name, inputs)
    def generate_register_parameter_args(self):
        return ColumnSelectionParam.generate_register_parameter_args(self) + [ "tag='my-tag'" ]

class NumericColumnSelection(ColumnSelectionParam):
    'numeric input column selection (combobox)'
    def __init__(self, param_name, inputs):
        ColumnSelectionParam.__init__(self, 'NUMERIC_COLUMN_SELECTION', param_name, inputs)

class StrColumnSelection(ColumnSelectionParam):
    'text (string) input column selection (combobox)'
    def __init__(self, param_name, inputs):
        ColumnSelectionParam.__init__(self, 'STRING_COLUMN_SELECTION', param_name, inputs)

class FloatColumnSelection(ColumnSelectionParam):
    'float input column selection (combobox)'
    def __init__(self, param_name, inputs):
        ColumnSelectionParam.__init__(self, 'FLOAT_COLUMN_SELECTION', param_name, inputs)

CUSTOM_COMBO_TOPLEVEL_CODE = '''\
DAYS = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
         'Saturday', 'Sunday' ]
'''

CUSTOM_COMBO_METHOD = '''\
# Sample code generating values for our combo parameter
def get_combo_days(self):
    # This method must return a list of tuples.
    # Each tuple should have the form: (<integer-id>, <string-label>).
    # The GUI will use <string-label> for displaying the combo items.
    # When the user selects an item, the 'value' attribute of this
    # combo parameter (i.e. self.value) will be set to the associated
    # <integer-id>.
    return list(enumerate(DAYS))
'''

class ComboParameter(Param):
    'other kind of combobox'
    NEXT_COMBO_NUM = 1
    def __init__(self, param_name, inputs):
        Param.__init__(self, 'COMBO', param_name, inputs)
        self.num = ComboParameter.NEXT_COMBO_NUM
        ComboParameter.NEXT_COMBO_NUM += 1
    def generate_register_parameter_args(self):
        return Param.generate_register_parameter_args(self) + [
            "get_possible_items=self.get_combo_days"
        ]
    @classmethod
    def needs_one_input(cls):
        return False
    def generate_top_level_code(self):
        return CUSTOM_COMBO_TOPLEVEL_CODE
    @property
    def custom_method(self):
        return CUSTOM_COMBO_METHOD

PARAM_CLASSES = [
    TagBasedColumnSelection,
    NumericColumnSelection,
    StrColumnSelection,
    FloatColumnSelection,
    ComboParameter
]

def generate_param_import_lines(params):
    return sum((param.get_imports() for param in params), ())

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
