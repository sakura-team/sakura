import Orange, sys
from remote_pdb import RemotePdb

class DelayedResultTableIterator(object):
    def __init__(self, drt):
        self.op_iter = drt.op.__iter__()
        self.domain = drt.domain
    def next(self):
        #RemotePdb('127.0.0.1', 4444).set_trace()
        v = self.op_iter.next()
        return Orange.data.Instance(
                self.domain, list(v))

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
        row = self.op.get_output(key)
        return Orange.data.Instance(
                self.domain, list(row))
    def __nonzero__(self):
        # if we have a 1st element, we return True
        # and False otherwise
        for row in self:
            return True
        return False
