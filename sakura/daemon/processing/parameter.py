import numpy as np
from sakura.common.tools import ObservableEvent
from sakura.common.cache import cache_result
from sakura.common.errors import ParameterException, InputUncompatible

# Parameter implementation.
class Parameter(object):
    def __init__(self, gui_type, label):
        self.gui_type = gui_type
        self.label = label
        self.on_change = ObservableEvent()
        self.on_auto_fill = ObservableEvent()
        self.requested_value = None
        self.value = None

    def get_value(self):
        return self.value

    def selected(self):
        return self.value != None

    def unset_value(self):
        old_val = self.value
        self.value = None
        if old_val != None:
            self.on_change.notify()

    def pack_base(self):
        self.recheck()
        info = dict(
            gui_type = self.gui_type,
            label = self.label
        )
        if self.selected():
            info.update(value = self.get_gui_value())
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

    def check_input_compatible(self):
        print('check_input_compatible() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def check_valid(self, value):
        print('check_valid() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def get_gui_value(self):
        print('get_gui_value() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def decode_gui_value(self, gui_value):
        print('decode_gui_value() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def recheck(self):
        # if we can now set the value requested by the user, do it
        if self.requested_value is not None and self.requested_value != self.value:
            if self.check_valid(self.requested_value):
                self.value = self.requested_value
                print(self.__class__.__name__ + ' recheck -- setting value ' + str(self.value) + ' because of requested value')
                self.on_change.notify()
                return self.value
        # if current value became invalid, unset it
        changed, auto_filled = False, False
        if not self.check_valid(self.value):
            print(self.__class__.__name__ + ' recheck -- discarding value ' + str(self.value) + ' (invalid)')
            self.value = None
            changed = True
        # if value is not set and no value was requested yet, try to set it automatically
        if self.value is None and self.requested_value is None:
            print(self.__class__.__name__ + ' recheck -- calling auto-fill')
            if self.auto_fill():
                changed, auto_filled = True, True
        print(self.__class__.__name__ + ' recheck -- returning value ' + str(self.value))
        if changed:
            print(self.__class__.__name__ + ' notify change!')
            self.on_change.notify()
        if auto_filled:
            print(self.__class__.__name__ + ' notify auto-fill!')
            self.on_auto_fill.notify()
        return self.value

    def set_requested_value(self, value):
        print(self.__class__.__name__ + ' set_requested_value ' + str(value))
        self.requested_value = value

    def set_requested_gui_value(self, gui_value):
        print(self.__class__.__name__ + ' set_requested_gui_value ' + str(gui_value))
        self.requested_value = self.decode_gui_value(gui_value)

class ComboParameter(Parameter):
    def __init__(self, label):
        super().__init__('COMBO', label)
    def pack(self):
        info = self.pack_base()
        try:
            info.update(possible_values = self.get_possible_labels())
        except ParameterException as e:
            info.update(issue = e.get_issue_name())
        return info
    def auto_fill(self):
        for value in self.get_possible_values():
            self.value = value   # take first value if any
            return True
        return False
    def get_possible_values(self):
        return (value for value, label in self.get_possible_items())
    def get_possible_labels(self):
        return (label for value, label in self.get_possible_items())
    def check_valid(self, value):
        if value is None:
            return True
        if value in self.get_possible_values():
            return True
        # value may have become invalid
        # (e.g. the value of another parameter changed the set of possible values)
        return False
    def get_possible_items(self):
        print('get_possible_items() must be implemented in ComboParameter subclasses.')
        raise NotImplementedError
    def get_gui_value(self):
        # gui value is the index in the combo
        if self.value is None:
            return None
        for i, val in enumerate(self.get_possible_values()):
            if val == self.value:
                return i
    def decode_gui_value(self, gui_value):
        for i, val in enumerate(self.get_possible_values()):
            if i == gui_value:
                return val

class ColumnSelectionParameter(ComboParameter):
    def __init__(self, label, plug, condition):
        super().__init__(label)
        self.plug = plug
        self.condition = condition
        self.plug.on_change.subscribe(self.notify_input_plug_change)
    def notify_input_plug_change(self):
        self.recheck()
    def is_linked_to_plug(self, plug):
        return self.plug == plug
    def check_input_compatible(self):
        for col_info in self.matching_columns():
            return True # OK, we have at least one value
        return False    # no matching column
    def matching_columns(self):
        if not self.plug.connected():
            return
        for col_idx, column_info in enumerate(self.plug.get_columns_info()):
            if self.condition(*column_info):
                input_plug_ok = True
                yield (col_idx,) + column_info + (str(column_info),)
    def get_possible_items(self):
        for col_idx, col_label, col_type, col_tags, col_info_str in self.matching_columns():
            value = col_info_str
            label = '%s (of %s)' % (col_label, self.plug.label)
            yield value, label
    @property
    def col_index(self):
        if self.value is None:
            return None
        for col_idx, col_label, col_type, col_tags, col_info_str in self.matching_columns():
            if col_info_str == self.value:
                return col_idx

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
