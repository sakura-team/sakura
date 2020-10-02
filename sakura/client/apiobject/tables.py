from sakura.client.apiobject.base import APIObjectBase
from sakura.client.resultset import ResultSet

class APITable:
    _known = {}
    def __new__(cls, remote_api, table_info):
        table_id = table_info['table_id']
        if table_id not in APITable._known:
            remote_obj = remote_api.tables[table_id]
            class APITableImpl(APIObjectBase):
                __doc__ = 'Sakura Table: ' + table_info['name']
                def get_rows(self, row_start, row_end):
                    """Query a range of table rows"""
                    return remote_obj.get_rows(row_start, row_end)
                @property
                def _resultset(self):
                    if not hasattr(self, '_internal_resultset'):
                        it = remote_obj.chunks()
                        self._internal_resultset = ResultSet(self.dtype, it)
                    return self._internal_resultset
                def _discard_resultset(self):
                    if hasattr(self, '_internal_resultset'):
                        delattr(self, '_internal_resultset')
                def snapshot(self):
                    """Return set of rows already fetched"""
                    return self._resultset.snapshot()
                def show(self):
                    """View table data interactively"""
                    return self._resultset.show()
                def data(self):
                    """Download full table data"""
                    return self._resultset.data()
                @property
                def _preview(self):
                    return repr(self._resultset)
                def __get_remote_info__(self):
                    return remote_obj.info()
            APITable._known[table_id] = APITableImpl()
        return APITable._known[table_id]
