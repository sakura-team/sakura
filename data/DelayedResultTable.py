import Orange, sys
from itertools import izip
from remote_pdb import RemotePdb

def to_discrete(*args):
    return Orange.feature.Discrete

def to_continuous(*args):
    return Orange.feature.Continuous

def to_string(*args):
    return Orange.feature.String

def to_enum(operator, out_id, col_label):
    values = operator.describe_enum(out_id, col_label)
    return lambda label: \
            Orange.feature.Discrete(label, values=values)

def do_nothing(feature):
    return lambda v: v

def int_to_discrete(feature):
    def f(v):
        str_v = str(v)
        feature.add_value(str_v)
        return str_v
    return f

TYPE_TO_FEATURE = {
    'enum': (to_enum, do_nothing),
    'int': (to_discrete, int_to_discrete),
    'float': (to_continuous, do_nothing),
    'str': (to_string, do_nothing)
}

def create_feature(operator, out_id, col_label, col_type):
    func = TYPE_TO_FEATURE[col_type][0](operator, out_id, col_label)
    return func(col_label)

def create_filter(col_type, feature):
    func = TYPE_TO_FEATURE[col_type][1]
    return func(feature)

def apply_filters(filters, row):
    for f, val in izip(filters, row):
        yield f(val)

def analyse_output(operator, out_id):
    output_desc = operator.describe_output(out_id)
    for col_label, col_type in output_desc:
        feature = create_feature(operator, out_id, col_label, col_type)
        value_filter = create_filter(col_type, feature)
        yield (feature, value_filter)

def format_as_orange_instance(domain, filters, row):
    return Orange.data.Instance(
                domain,
                list(apply_filters(filters, row)))

class DelayedResultTableIterator(object):
    def __init__(self, drt):
        self.op_iter = drt.op.__iter__()
        self.filters = drt.filters
        self.domain = drt.domain
    def next(self):
        return format_as_orange_instance(
            self.domain,
            self.filters,
            self.op_iter.next()
        )

class DelayedResultTable(Orange.data.Table):
    def __new__(cls, operator, out_id):
        output_analysis = tuple(analyse_output(operator, out_id))
        features, filters = zip(*output_analysis)
        domain = Orange.data.Domain(list(features), False)
        self = Orange.data.Table.__new__(cls, domain)
        self.filters = filters
        return self
    def __init__(self, operator, out_id):
        Orange.data.Table.__init__(self, self.domain)
        self.op = operator
    def __iter__(self):
        return DelayedResultTableIterator(self)
    def __len__(self):
        return self.op.get_output_len()
    def __getitem__(self, key):
        if type(key) == str:
            key = self.domain.index(key)
        return format_as_orange_instance(
            self.domain,
            self.filters,
            self.op.get_output(key)
        )
    def __nonzero__(self):
        # if we have a 1st element, we return True
        # and False otherwise
        for row in self:
            return True
        return False
