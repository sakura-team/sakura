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

    def pack_base(self):
        info = dict(
            gui_type = self.gui_type,
            label = self.label
        )
        if self.selected():
            info.update(value = self.get_value_serializable())
        else:
            info.update(value = None)
        return info

    def pack(self):
        print('pack() must be implemented in Parameter subclasses.')
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
    def pack(self):
        info = self.pack_base()
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
        for col_idx, column_info in enumerate(self.stream.get_columns_info()):
            if self.condition(*column_info):
                yield (col_idx,) + column_info
    def get_possible_values(self):
        if not self.stream.connected():
            raise ParameterException(Issue.InputNotConnected)
        return list('%s (of %s)' % (col_label, self.stream.label) \
                    for col_idx, col_label, col_type, col_tags in \
                        self.matching_columns())
    def set_value(self, poss_idx):
        if not self.stream.connected():
            raise ParameterException(Issue.InputNotConnected)
        # raw_value is the index of the column in the possible values
        self.raw_value = poss_idx
        # value is the index of the column in the stream
        col_idx = tuple(self.matching_columns())[poss_idx][0]
        self.value = col_idx
    def unset_value(self):
        self.raw_value = None
        self.value = None
    def get_value_serializable(self):
        return self.raw_value

class TagBasedColumnSelection(ColumnSelectionParameter):
    def __init__(self, label, stream, tag):
        def condition(col_label, col_type, col_tags):
            return tag in col_tags
        ColumnSelectionParameter.__init__(self, label, stream, condition)

class TypeBasedColumnSelection(ColumnSelectionParameter):
    def __init__(self, label, stream, cls):
        def condition(col_label, col_type, col_tags):
            return np.issubdtype(col_type, cls)
        ColumnSelectionParameter.__init__(self, label, stream, condition)
    @staticmethod
    def adapt_to_cls(cls):
        class AdaptedTypeBasedColumnSelection(TypeBasedColumnSelection):
            def __init__(self, label, stream):
                super().__init__(label, stream, cls)
        return AdaptedTypeBasedColumnSelection

NumericColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.number)
StrColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.str)
FloatColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.float)
