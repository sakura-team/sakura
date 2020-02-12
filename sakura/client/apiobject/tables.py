from sakura.client.apiobject.base import APIObjectBase

class APITable:
    def __new__(cls, remote_api, table_info):
        table_id = table_info['table_id']
        remote_obj = remote_api.tables[table_id]
        class APITableImpl(APIObjectBase):
            __doc__ = 'Sakura Table: ' + table_info['name']
            def get_rows(self, row_start, row_end):
                """Query a range of table rows"""
                return remote_obj.get_rows(row_start, row_end)
            def __get_remote_info__(self):
                return remote_obj.info()
        return APITableImpl()
