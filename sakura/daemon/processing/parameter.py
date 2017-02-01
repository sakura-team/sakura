import numbers
from enum import Enum

ParameterIssue = Enum('ParameterIssue', 'InputNotConnected')

# Parameter implementation.
class Parameter(object):
    def __init__(self, gui_type, label):
        self.gui_type = gui_type
        self.label = label
        self.value = None

    def selected(self):
        return self.value != None

    # redirect other accesses to the selected value
    def __getattr__(self, attr):
        if not self.selected():
            return None
        return getattr(self.value, attr)

    def get_info_serializable_base(self):
        info = dict(
            gui_type = self.gui_type,
            label = self.label
        )
        if self.selected():
            info.update(value = self.get_value_serializable())
        else:
            info.update(value = None)
        return info

    def get_info_serializable(self):
        print('get_info_serializable() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def auto_fill(self):
        print('auto_fill() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    # override in subclass if needed.
    def set_value(self, value):
        self.value = value

    # override in subclass if needed.
    def get_value_serializable(self):
        return self.value

class ComboParameter(Parameter):
    def __init__(self, label):
        super().__init__('COMBO', label)
    def get_info_serializable(self):
        info = self.get_info_serializable_base()
        possible_values = self.get_possible_values()
        if isinstance(possible_values, ParameterIssue):
            # get the name of the ParameterIssue enum
            info.update(issue = possible_values.name)
        else:
            info.update(possible_values = possible_values)
        return info
    def auto_fill(self):
        if not self.selected():
            possible = self.get_possible_values()
            if not isinstance(possible, ParameterIssue) and \
                    len(possible) > 0:
                self.set_value(possible[0][0])
    def get_possible_values(self):
        print('get_possible_values() must be implemented in ComboParameter subclasses.')
        raise NotImplementedError

class ColumnSelectionParameter(ComboParameter):
    def __init__(self, label, table, condition):
        super().__init__(label)
        self.table = table
        self.condition = condition
        self.raw_value = None
    def get_possible_values(self):
        if self.table.connected():
            possible = []
            for idx, column in enumerate(self.table.columns):
                if self.condition(column):
                    label = '%s (of %s)' % (column.label, self.table.label)
                    possible.append((idx, label))
            return possible
        else:
            return ParameterIssue.InputNotConnected
    def set_value(self, idx):
        self.raw_value = idx
        self.value = self.table.columns[idx]
    def get_value_serializable(self):
        return self.raw_value

def TypeBasedColumnSelection(table, cls):
    class CustomParameterClass(ColumnSelectionParameter):
        def __init__(self, label):
            def condition(column):
                return issubclass(column.type, cls)
            ColumnSelectionParameter.__init__(self, label, table, condition)
    return CustomParameterClass

def NumericColumnSelection(table):
    return TypeBasedColumnSelection(table, numbers.Number)

def StrColumnSelection(table):
    return TypeBasedColumnSelection(table, str)

