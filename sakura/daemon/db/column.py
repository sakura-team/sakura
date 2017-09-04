import numpy as np

class DBColumn:
    def __init__(self,  table_name,
                        col_name,
                        np_type,
                        col_name_wrapper = '%s',
                        value_wrapper = '%s',
                        tags = ()):
        self.table_name = table_name
        self.col_name = col_name
        self.np_dtype = np.dtype(np_type)
        self.col_name_wrapper = col_name_wrapper
        self.value_wrapper = value_wrapper
        self.tags = list(tags)
        self.qualified_name = table_name + "." + col_name
    def pack(self):
        return (self.col_name, str(self.np_dtype), self.tags)

