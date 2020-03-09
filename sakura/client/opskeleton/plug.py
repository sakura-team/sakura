from sakura.client.opskeleton.tools import get_suffixes
from sakura.client.opskeleton.param import ComboParameter, NumericColumnSelection, FloatColumnSelection

PLUG_COMMENT_PATTERN = '# %(plug_type)ss'

PLUG_DECL_PATTERN = '''\
self.%(plug_name)s = self.register_%(plug_type)s('%(plug_desc)s')\
'''

class Plug:
    def __init__(self, plug_type, plug_name, plug_desc):
        self.type = plug_type
        self.name = plug_name
        self.desc = plug_desc
    @property
    def decl_pattern(self):
        return PLUG_DECL_PATTERN % dict(
            plug_name = self.name,
            plug_type = self.type,
            plug_desc = self.desc
        )
    @property
    def custom_method(self):
        return ''

    @property
    def custom_imports(self):
        return ()

CUSTOM_COMBO_OUTPUT_DECL_PATTERN = '''\
days_output_source = ComputedSource('Days', self.compute_days)
days_output_source.add_column('Year', int)
days_output_source.add_column('Month', str)
days_output_source.add_column('Day of month', int)
self.register_output(
        label = 'Days',
        source = days_output_source)
'''

CUSTOM_COMBO_OUTPUT_CUSTOM_CODE = '''\
# This function serves as a data source for the output
# labelled 'Days'. It streams (<year>,<month>,<day-of-month>)
# tuples, selecting only those corresponding to the day
# of the week specified by our custom combo parameter.
def compute_days(self):
    selected_week_day = self.%(param_name)s.value
    one_day = datetime.timedelta(days=1)
    t = datetime.datetime.today()
    while True:
        if t.weekday() == selected_week_day:
            year = int(t.strftime('%%Y'))
            month = t.strftime('%%b')
            day_of_month = int(t.strftime('%%d'))
            # send this tuple to output
            yield (year, month, day_of_month)
        t += one_day
'''

MEAN_OUTPUT_DECL_PATTERN = '''\
mean_output_source = ComputedSource('Mean', self.compute_mean)
mean_output_source.add_column('Mean value', float)
self.register_output(
        label = 'Mean',
        source = mean_output_source)
'''

MEAN_OUTPUT_CUSTOM_CODE = '''\
# This function serves as a data source for the output
# labelled 'Mean'.
# This stream has only one column, of type "float", as indicated
# in 'mean_output_source' definition above.
# It actually streams a single tuple (<mean-value>,)
# indicating the result of the calculation.
def compute_mean(self):
    column = self.%(param_name)s.column
    res = 0
    num = 0
    for chunk in column.chunks():
        res += chunk.sum()
        num += chunk.size
    mean = float(res)/num
    # our output has only 1 row and 1 column
    yield (mean,)
'''

class CustomComboOutput(Plug):
    def __init__(self, combo_param, *args):
        Plug.__init__(self, *args)
        self.combo_param = combo_param
    @staticmethod
    def instanciate(inputs, params, args):
        for param in params:
            if isinstance(param, ComboParameter):
                return CustomComboOutput(param, *args)
    @property
    def decl_pattern(self):
        return CUSTOM_COMBO_OUTPUT_DECL_PATTERN
    @property
    def custom_method(self):
        return (CUSTOM_COMBO_OUTPUT_CUSTOM_CODE % dict(
            param_name = self.combo_param.name
        )).strip()
    @property
    def custom_imports(self):
        return ('import datetime', 'from sakura.daemon.processing.source import ComputedSource')

class MeanOutput(Plug):
    def __init__(self, param, *args):
        Plug.__init__(self, *args)
        self.param = param
    @staticmethod
    def instanciate(inputs, params, args):
        for param in params:
            if isinstance(param, (NumericColumnSelection, FloatColumnSelection)):
                return MeanOutput(param, *args)
    @property
    def decl_pattern(self):
        return MEAN_OUTPUT_DECL_PATTERN
    @property
    def custom_method(self):
        return (MEAN_OUTPUT_CUSTOM_CODE % dict(
            param_name = self.param.name,
            input_name = self.param.linked_input.name
        )).strip()
    @property
    def custom_imports(self):
        return ('from sakura.daemon.processing.source import ComputedSource',)

def generate_plugs(num, plug_type, factory=Plug):
    if num == 0:
        return
    suffixes = get_suffixes(num)
    for i in range(num):
        suffix = suffixes[i]
        plug_name = plug_type + '_plug' + suffix
        plug_desc = plug_type.capitalize() + suffix.replace('_', ' ')
        yield factory(plug_type, plug_name, plug_desc)

def generate_input_plugs(num):
    return list(generate_plugs(num, 'input'))

class OutputPlugFactory:
    def __init__(self, inputs, params):
        self.inputs = inputs
        self.params = params
        self.possible_types = [ CustomComboOutput, MeanOutput ]
        self.default_type = Plug
    def __call__(self, *args):
        for cls in self.possible_types.copy():
            instance = cls.instanciate(self.inputs, self.params, args)
            if instance is not None:
                self.possible_types.remove(cls)
                return instance
        # by default return a standalone output plug
        return Plug(*args)

def generate_output_plugs(num, inputs, params):
    factory = OutputPlugFactory(inputs, params)
    return list(generate_plugs(num, 'output', factory))

def generate_plugs_declaration(plugs):
    if len(plugs) == 0:
        return []
    plug_type = plugs[0].type
    lines = [ PLUG_COMMENT_PATTERN % dict(plug_type = plug_type) ]
    lines.extend(p.decl_pattern.strip() for p in plugs)
    return lines
