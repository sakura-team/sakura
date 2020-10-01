from sakura.common.errors import APIRequestError

class Condition:
    def __init__(self):
        self.prev = None
    def __and__(self, other):
        other.prev = self
        return other    # to continue chaining
    def list(self):
        l = []
        cond = self
        while cond is not None:
            l.append(cond)
            cond = cond.prev
        return l

class SingleColumnFilter(Condition):
    def __init__(self, column, op, value):
        Condition.__init__(self)
        self.column = column
        self.op = op
        self.value = value
    def filtered_sources(self, *sources):
        new_sources = []
        could_apply = False
        for source in sources:
            if self.column in source.columns:
                source = source.filtered(self.column, self.op, self.value)
                could_apply = True
            new_sources.append(source)
        if could_apply:
            return tuple(new_sources)
        else:
            raise APIRequestError('Column filter does not apply to specified sources.')

class JoinCondition(Condition):
    def __init__(self, left_col, op, right_col):
        Condition.__init__(self)
        self.left_col = left_col
        self.right_col = right_col
        self.op = op
