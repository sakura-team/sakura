import Orange, sys
from itertools import izip
from remote_pdb import RemotePdb

def discrete_values_formatter(domain, row):
    for f, val in izip(domain, row):
        if f.var_type == f.Discrete:
            str_val = str(val)
            f.add_value(str_val)
            yield str_val
        else:
            yield val

def format_as_orange_instance(domain, row):
    return Orange.data.Instance(
                domain,
                list(discrete_values_formatter(domain, row)))

class DelayedResultTableIterator(object):
    def __init__(self, drt):
        self.op_iter = drt.op.__iter__()
        self.domain = drt.domain
    def next(self):
        return format_as_orange_instance(
            self.domain,
            self.op_iter.next()
        )

class DelayedResultTable(Orange.data.Table):
    def __new__(cls, operator, domain):
        return Orange.data.Table.__new__(cls, domain)
    def __init__(self, operator, domain):
        Orange.data.Table.__init__(self, domain)
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
            self.op.get_output(key)
        )
    def __nonzero__(self):
        # if we have a 1st element, we return True
        # and False otherwise
        for row in self:
            return True
        return False
