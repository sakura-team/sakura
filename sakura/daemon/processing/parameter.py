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
        self.on_change = lambda: None

    def selected(self):
        self.recheck()
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

    def is_linked_to_plug(self, plug):
        print('is_linked_to_plug() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    # override in subclass if needed.
    def set_value(self, value):
        self.value = value
        self.recheck()
        self.on_change()

    # override in subclass if needed.
    def unset_value(self):
        self.value = None
        self.on_change()

    # override in subclass if needed.
    def recheck(self):
        pass

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
    def recheck(self):
        if self.value is not None:
            # value is selected...
            if self.value >= len(self.get_possible_values()):
                # ... but it became invalid
                # (e.g. the value of another parameter changed the set of possible values)
                self.unset_value()
    def get_possible_values(self):
        print('get_possible_values() must be implemented in ComboParameter subclasses.')
        raise NotImplementedError

class ColumnSelectionParameter(ComboParameter):
    def __init__(self, label, plug, condition):
        super().__init__(label)
        self.plug = plug
        self.condition = condition
    def is_linked_to_plug(self, plug):
        return self.plug == plug
    def matching_columns(self):
        for col_idx, column_info in enumerate(self.plug.get_columns_info()):
            if self.condition(*column_info):
                yield (col_idx,) + column_info
    def get_possible_values(self):
        if not self.plug.connected():
            raise ParameterException(Issue.InputNotConnected)
        return list('%s (of %s)' % (col_label, self.plug.label) \
                    for col_idx, col_label, col_type, col_tags in \
                        self.matching_columns())
    @property
    def col_index(self):
        if self.value is None:
            return None
        # self.value is the index of the column in the possible values
        # each possible value is a tuple whose first item is the col index
        return tuple(self.matching_columns())[self.value][0]

class TagBasedColumnSelection(ColumnSelectionParameter):
    def __init__(self, label, plug, tag):
        def condition(col_label, col_type, col_tags):
            return tag in col_tags
        ColumnSelectionParameter.__init__(self, label, plug, condition)

class TypeBasedColumnSelection(ColumnSelectionParameter):
    def __init__(self, label, plug, cls):
        def condition(col_label, col_type, col_tags):
            return np.issubdtype(col_type, cls)
        ColumnSelectionParameter.__init__(self, label, plug, condition)
    @staticmethod
    def adapt_to_cls(cls):
        class AdaptedTypeBasedColumnSelection(TypeBasedColumnSelection):
            def __init__(self, label, plug):
                super().__init__(label, plug, cls)
        return AdaptedTypeBasedColumnSelection

NumericColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.number)
StrColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.str)
FloatColumnSelection = TypeBasedColumnSelection.adapt_to_cls(np.float)
