from sakura.client.apiobject.base import APIObjectBase

class APITable:
    def __new__(cls, remote_api, table_id):
        remote_obj = remote_api.tables[table_id]
        def get_info():
            return remote_obj.info()
        class APITableImpl(APIObjectBase):
            __doc__ = 'Sakura Table: ' + get_info()['name']
            def get_rows(self, row_start, row_end):
                """Query a range of table rows"""
                return remote_obj.get_rows(row_start, row_end)
            def __doc_attrs__(self):
                return get_info().items()
            def __getattr__(self, attr):
                info = get_info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APITableImpl()
