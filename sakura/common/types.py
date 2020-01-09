import numpy as np

# Strings whose length is known to be lower than NUMPY_EMBEDDED_STR_MAX_LEN
# will be encoded directly in numpy arrays.
# Others will be saved as an object pointer in numpy arrays.
NUMPY_EMBEDDED_STR_MAX_LEN = 16
SAKURA_INTEGER_TYPES = ('int8', 'int16', 'int32', 'int64',
                        'uint8', 'uint16', 'uint32', 'uint64')
SAKURA_FLOATING_TYPES = ('float32', 'float64')
SAKURA_NUMERIC_TYPES = SAKURA_INTEGER_TYPES + SAKURA_FLOATING_TYPES
SAKURA_NUMPY_TYPES = SAKURA_NUMERIC_TYPES + ('bool',)

def sakura_type_to_np_dtype(col_type, **params):
    if col_type == 'date':
        return np.dtype('float64')
    if col_type == 'opaque':
        return np.dtype(object)
    if col_type in ('string', 'geometry'):
        max_len = params.get('max_length')
        if max_len is not None and max_len < NUMPY_EMBEDDED_STR_MAX_LEN:
            return np.dtype(('str', max_len))
        else:
            return np.dtype(object)
    if col_type in SAKURA_NUMPY_TYPES:
        return np.dtype(col_type)
    raise NotImplementedError('Do not know how to translate sakura type %s to a numpy dtype.' % repr(col_type))

def np_dtype_to_sakura_type(dt):
    if dt.name in SAKURA_NUMPY_TYPES:
        return dt.name, {}
    if dt.name == 'object':
        return 'opaque', {}
    if dt.type == np.str_:
        length_chars = str(dt).strip('<>U')
        if length_chars == '':
            max_length = 0
        else:
            max_length = int(length_chars)
        if (max_length == 0):
            return 'string', {}     # unknown length
        else:
            return 'string', { 'max_length': max_length }
    raise NotImplementedError('Do not know how to translate %s to a sakura type.' % repr(dt))

def verify_sakura_type_conversion(old_type, new_type):
    if (old_type, new_type) not in (
            ('opaque', 'string'),
            ('opaque', 'geometry'),
            ('string', 'geometry'),
            ('float64', 'date')):
        raise APIRequestError("Cannot convert sakura type '%s' to '%s'!", (old_type, new_type))

def is_numeric_type(sakura_type):
    return sakura_type in SAKURA_NUMERIC_TYPES

def is_floating_type(sakura_type):
    return sakura_type in SAKURA_FLOATING_TYPES
