import numpy as np
from sakura.common.tools import ObservableEvent, StatusMixin
from sakura.common.cache import cache_result
from sakura.common.errors import ParameterException, InputUncompatible
from sakura.common.types import is_numeric_type, is_floating_type

# Parameter implementation.
class Parameter(StatusMixin):
    def __init__(self, op, gui_type, label):
        self.op = op
        self.gui_type = gui_type
        self.label = label
        self.on_change = ObservableEvent()
        self.on_auto_fill = ObservableEvent()
        self.requested_value = None
        self.value = None
        self.is_setup = False
        self.on_change.subscribe(lambda: self.op.notify_parameter_change(self))

    @property
    def check_mode(self):
        return self.op.check_mode

    def setup(self, requested_value, auto_fill_cb):
        print(self.__class__.__name__ + ' setup -- requested value ' + str(requested_value) + ' + auto-fill cb')
        self.requested_value = requested_value
        self.on_auto_fill.subscribe(auto_fill_cb)
        self.is_setup = True
        self.recheck()

    def get_value(self):
        return self.value

    def selected(self):
        return self.value != None

    def unset_value(self):
        old_val = self.value
        self.value = None
        if old_val != None and not self.check_mode:
            self.on_change.notify()

    def pack_base(self):
        info = dict(
            gui_type = self.gui_type,
            label = self.label,
            **self.pack_status_info()
        )
        if self.selected():
            info.update(value = self.get_gui_value())
        else:
            info.update(value = None)
        return info

    @property
    def enabled(self):
        return True     # override in subclass if needed

    def pack(self):
        print('pack() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def auto_fill(self):
        print('auto_fill() must be implemented in Parameter subclasses.')
        raise NotImplementedError

    def is_linked_to_plug(self, plug):
        return False    # override in subclass if parameter is linked to a given input plug

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
        if not self.is_setup:
            return None
        # if we can now set the value requested by the user, do it
        if self.requested_value is not None and self.requested_value != self.value:
            if self.check_valid(self.requested_value):
                self.value = self.requested_value
                print(self.__class__.__name__ + ' recheck -- setting value ' + str(self.value) + ' because of requested value')
                if not self.check_mode:
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
        if auto_filled and not self.check_mode:
            print(self.__class__.__name__ + ' notify auto-fill!')
            self.on_auto_fill.notify()
        if changed and not self.check_mode:
            print(self.__class__.__name__ + ' notify change!')
            self.on_change.notify()
        return self.value

    def set_requested_value(self, value):
        print(self.__class__.__name__ + ' set_requested_value ' + str(value))
        self.requested_value = value

    def set_requested_gui_value(self, gui_value):
        print(self.__class__.__name__ + ' set_requested_gui_value ' + str(gui_value))
        self.requested_value = self.decode_gui_value(gui_value)

class ComboParameter(Parameter):
    def __init__(self, op, label, get_possible_items=None):
        super().__init__(op, 'COMBO', label)
        if get_possible_items is not None:
            self.get_possible_items = get_possible_items
    def pack(self):
        info = self.pack_base()
        try:
            info.update(possible_values = self.get_possible_labels())
        except ParameterException as e:
            info.update(issue = e.get_issue_name())
        return info
    @property
    def enabled(self):
        return self.at_least_one_possible_value()
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        return 'This parameter currently has no possible value.'
    @property
    def warning_message(self):
        if self.value is not None:
            # everything is fine => no warning message
            raise AttributeError
        if not self.at_least_one_possible_value():
            # parameter is actually disabled, reason is given in self.disabled_message
            raise AttributeError
        if self.requested_value is not None:
            return 'Previously selected value is no longer available!'
        return 'No value is selected!'
    def at_least_one_possible_value(self):
        for value in self.get_possible_values():
            return True
        return False
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
    def __init__(self, op, label, plug, condition):
        super().__init__(op, label)
        self.plug = plug
        self.condition = condition
        self.plug.on_change.subscribe(self.notify_input_plug_change)
    def notify_input_plug_change(self):
        self.recheck()
    def is_linked_to_plug(self, plug):
        return self.plug == plug
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        if not self.plug.connected():
            return 'Input is not connected.'
        elif self.plug.source is None:
            return 'Input is not ready.'
        else:
            return 'Input is not compatible.'
    def check_input_compatible(self):
        return self.at_least_one_possible_value()
    def matching_columns(self):
        if not self.plug.enabled:
            return
        for col_info in self.plug.get_columns_info():
            col_path, column_info = col_info[0], col_info[1:]
            if self.condition(*column_info):
                yield (col_path,) + column_info + (str(column_info),)
    def get_possible_items(self):
        if not self.plug.enabled:
            return
        source_label = self.plug.source.get_label()
        for col_path, col_label, col_type, col_tags, col_info_str in self.matching_columns():
            value = col_info_str
            label = '%s (of %s)' % (col_label, source_label)
            yield value, label
    @property
    def col_index(self):
        # deprecated, use self.col_path property below (to handle subcolumns)
        col_path = self.col_path
        if self.col_path is None:
            return None
        return col_path[0]  # ignore the fact it may actually be a subcolumn
    @property
    def col_path(self):
        if self.value is None:
            return None
        for col_path, col_label, col_type, col_tags, col_info_str in self.matching_columns():
            if col_info_str == self.value:
                return col_path
    @property
    def column(self):
        col_path = self.col_path
        if col_path is None:
            return None
        return self.plug.source.columns[col_path]
    @staticmethod
    def adapt_with_condition(cond):
        class AdaptedColumnSelection(ColumnSelectionParameter):
            def __init__(self, op, label, plug):
                super().__init__(op, label, plug, cond)
        return AdaptedColumnSelection

# Cannot use adapt_with_condition() for this one, since the __init__() function
# has one more argument.
class TagBasedColumnSelection(ColumnSelectionParameter):
    def __init__(self, op, label, plug, tag):
        ColumnSelectionParameter.__init__(self, op, label, plug,
            lambda col_label, col_type, col_tags: tag in col_tags
        )

AnyColumnSelection = ColumnSelectionParameter.adapt_with_condition(
    lambda col_label, col_type, col_tags: True
)

NumericColumnSelection = ColumnSelectionParameter.adapt_with_condition(
    lambda col_label, col_type, col_tags: is_numeric_type(col_type)
)

FloatColumnSelection = ColumnSelectionParameter.adapt_with_condition(
    lambda col_label, col_type, col_tags: is_floating_type(col_type)
)

StrColumnSelection = ColumnSelectionParameter.adapt_with_condition(
    lambda col_label, col_type, col_tags: col_type == 'string'
)

GeometryColumnSelection = ColumnSelectionParameter.adapt_with_condition(
    lambda col_label, col_type, col_tags: col_type == 'geometry'
)

PARAMETER_CLASSES = {
    'COMBO': ComboParameter,
    'TAG_BASED_COLUMN_SELECTION': TagBasedColumnSelection,
    'NUMERIC_COLUMN_SELECTION': NumericColumnSelection,
    'FLOAT_COLUMN_SELECTION': FloatColumnSelection,
    'STRING_COLUMN_SELECTION': StrColumnSelection,
    'GEOMETRY_COLUMN_SELECTION': GeometryColumnSelection,
    'ANY_COLUMN_SELECTION': AnyColumnSelection
}

def instanciate_parameter(op, param_type, label, *args, **kwargs):
    param_cls = PARAMETER_CLASSES.get(param_type)
    if param_cls is None:
        raise Exception('Allowed parameter types: ' + ', '.join(PARAMETER_CLASSES.keys()))
    return param_cls(op, label, *args, **kwargs)
