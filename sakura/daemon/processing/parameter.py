import numpy as np
from sakura.common.tools import ObservableEvent
from sakura.common.cache import cache_result
from sakura.common.errors import ParameterException, InputUncompatible

# Parameter implementation.
class Parameter(object):
    def __init__(self, gui_type, label):
        self.gui_type = gui_type
        self.label = label
        self.value = None
        self.on_change = ObservableEvent()
        self.requested_value = None

    def selected(self):
        return self.value != None

    def pack_base(self):
        self.recheck()
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

    @cache_result(2)    # do not call too often
    def recheck(self):
        # if we can now set the value requested by the user, do it
        if self.requested_value is not None and self.requested_value != self.value:
            if self.check_valid(self.requested_value):
                self.set_value(self.requested_value, user_request=False)
                return
        # if current value became invalid, unset it
        if not self.check_valid(self.value):
            self.unset_value(user_request=False)
        # if value is not set, try to set it automatically
        if self.value is None:
            self.auto_fill()

    def set_value(self, value, user_request=True):
        if user_request:
            self.requested_value = value
        if value != self.value and self.check_valid(value):
            self.value = value
            self.on_change.notify()

    def unset_value(self, user_request=True):
        self.set_value(None, user_request=user_request)

    # override in subclass if needed.
    def check_valid(self, value):
        return True

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
            if len(possible) > 0:
                self.set_value(0, user_request = False)
    def check_valid(self, value):
        if value is None:
            return True
        if value < len(self.get_possible_values()):
            return True
        # value may have became invalid
        # (e.g. the value of another parameter changed the set of possible values)
        return False
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
        if not self.plug.connected():
            return
        input_plug_ok = False
        for col_idx, column_info in enumerate(self.plug.get_columns_info()):
            if self.condition(*column_info):
                input_plug_ok = True
                yield (col_idx,) + column_info
        if not input_plug_ok:
            raise InputUncompatible()
    def get_possible_values(self):
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
