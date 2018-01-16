import numpy as np

# Strings whose length is known to be lower than NUMPY_EMBEDDED_STR_MAX_LEN
# will be encoded directly in numpy arrays.
# Others will be saved as an object pointer in numpy arrays.
NUMPY_EMBEDDED_STR_MAX_LEN = 16

SPECIAL_TYPES = {
    'date': 'float64'
}

def sakura_type_to_np_dtype(col_type, **params):
    if col_type in SPECIAL_TYPES:
        return SPECIAL_TYPES[col_type]
    elif col_type in ('string', 'geometry'):
        max_len = params.get('max_len')
        if max_len is not None and max_len < NUMPY_EMBEDDED_STR_MAX_LEN:
            return np.dtype(('str', max_len))
        else:
            return np.dtype(object)
    else:
        return np.dtype(col_type)
