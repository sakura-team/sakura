#import Orange

#class DelayedResultTable(Orange.data.Table):
class DelayedResultTable(object):
    def __init__(self, operator):
        self.op = operator
    def __iter__(self):
        return self.op.__iter__()
        
