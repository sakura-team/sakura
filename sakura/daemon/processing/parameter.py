import numbers

class ParameterIssue(object):
    InputNotConnected = 0
    def __init__(self, issue_type):
        self.issue_type = issue_type


# Parameter implementation.
class Parameter(object):
    IssueInputNotConnected = ParameterIssue(ParameterIssue.InputNotConnected)

    def __init__(self, label):
        self.label = label
        self.value = None

    def selected(self):
        return self.value != None

    # redirect other accesses to the selected value
    def __getattr__(self, attr):
        if not self.selected():
            return None
        return getattr(self.value, attr)

class ComboParameter(Parameter):
    pass

class ColumnSelectionParameter(ComboParameter):
    def __init__(self, label, table, condition):
        super().__init__(label)
        self.table = table
        self.condition = condition
    def get_possible_values(self):
        if self.table.connected():
            possible = []
            for idx, column in enumerate(self.table.columns):
                if self.condition(column):
                    label = '%s (of %s)' % (column.label, self.table.label)
                    possible.append((idx, label))
            return possible
        else:
            return Parameter.IssueInputNotConnected
    def select(self, idx):
        self.value = self.table.columns[idx]

def NumericColumnSelection(table):
    class CustomParameterClass(ColumnSelectionParameter):
        def __init__(self, label):
            def condition(column):
                return issubclass(column.type, numbers.Number)
            ColumnSelectionParameter.__init__(self, label, table, condition)
    return CustomParameterClass

