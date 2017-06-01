import numpy as np
from enum import Enum

Issue = Enum('ParameterIssue',
        'InputNotConnected NotSelected NoPossibleValues')

class ParameterException(Exception):
    def get_issue_name(self):
        # get the name of the Issue enum
        return self.args[0].name

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
            raise ParameterException(Issue.NotSelected)
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

    def is_linked_to_stream(self, stream):
        print('is_linked_to_stream() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    # override in subclass if needed.
    def set_value(self, value):
        self.value = value

    # override in subclass if needed.
    def unset_value(self):
        self.value = None

    # override in subclass if needed.
    def get_value_serializable(self):
        return self.value

class ComboParameter(Parameter):
    def __init__(self, label):
        super().__init__('COMBO', label)
    def get_info_serializable(self):
        info = self.get_info_serializable_base()
        try:
            possible_values = self.get_possible_values()
            info.update(possible_values = possible_values)
        except ParameterException as e:
            info.update(issue = e.get_issue_name())
        return info
    def auto_fill(self):
        if not self.selected():
            possible = self.get_possible_values()
            if len(possible) == 0:
                raise ParameterException(Issue.NoPossibleValues)
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
    def is_linked_to_stream(self, stream):
        return self.stream == stream
    def matching_columns(self):
        for idx, column in enumerate(self.stream.columns):
            if self.condition(column):
                yield column
    def get_possible_values(self):
        if not self.stream.connected():
            raise ParameterException(Issue.InputNotConnected)
        return list('%s (of %s)' % (column.label, self.stream.label) \
                    for column in self.matching_columns())
    def set_value(self, idx):
        if not self.stream.connected():
            raise ParameterException(Issue.InputNotConnected)
        # raw_value is the index of the column in the possible values
        self.raw_value = idx
        # value is the selected column
        self.value = tuple(self.matching_columns())[idx]
    def unset_value(self):
        self.raw_value = None
        self.value = None
    def get_value_serializable(self):
        return self.raw_value

def TagBasedColumnSelection(stream, tag):
    class CustomParameterClass(ColumnSelectionParameter):
        def __init__(self, label):
            def condition(column):
                return tag in column.tags
            ColumnSelectionParameter.__init__(self, label, stream, condition)
    return CustomParameterClass

def TypeBasedColumnSelection(stream, cls):
    class CustomParameterClass(ColumnSelectionParameter):
        def __init__(self, label):
            def condition(column):
                return np.issubdtype(column.type, cls)
            ColumnSelectionParameter.__init__(self, label, stream, condition)
    return CustomParameterClass

def NumericColumnSelection(stream):
    return TypeBasedColumnSelection(stream, np.number)

def StrColumnSelection(stream):
    return TypeBasedColumnSelection(stream, np.str)

def FloatColumnSelection(stream):
    return TypeBasedColumnSelection(stream, np.float)

