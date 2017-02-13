import numbers
from enum import Enum

ParameterIssue = Enum('ParameterIssue', 'InputNotConnected NotSelected')

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
            raise AttributeError
        return getattr(self.value, attr)

    # for case where self.value is iterable, we explicitly
    # forward the __iter__() method.
    # (by default it is not catched by __getattr__ because
    # it is a 'special method'.)
    def __iter__(self):
        if not self.selected():
            raise ParameterIssue.NotSelected
        return self.value.__iter__()

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
                self.set_value(0)
    def get_possible_values(self):
        print('get_possible_values() must be implemented in ComboParameter subclasses.')
        raise NotImplementedError

class ColumnSelectionParameter(ComboParameter):
    def __init__(self, label, stream, condition):
        super().__init__(label)
        self.stream = stream
        self.condition = condition
        self.raw_value = None
    def matching_columns(self):
        for idx, column in enumerate(self.stream.columns):
            if self.condition(column):
                yield column
    def get_possible_values(self):
        if not self.stream.connected():
            return ParameterIssue.InputNotConnected
        return list('%s (of %s)' % (column.label, self.stream.label) \
                    for column in self.matching_columns())
    def set_value(self, idx):
        if not self.stream.connected():
            raise ParameterIssue.InputNotConnected
        # raw_value is the index of the column in the possible values
        self.raw_value = idx
        # value is the selected column
        self.value = tuple(self.matching_columns())[idx]
    def get_value_serializable(self):
        return self.raw_value

def TypeBasedColumnSelection(stream, cls):
    class CustomParameterClass(ColumnSelectionParameter):
        def __init__(self, label):
            def condition(column):
                return issubclass(column.type, cls)
            ColumnSelectionParameter.__init__(self, label, stream, condition)
    return CustomParameterClass

def NumericColumnSelection(stream):
    return TypeBasedColumnSelection(stream, numbers.Number)

def StrColumnSelection(stream):
    return TypeBasedColumnSelection(stream, str)

