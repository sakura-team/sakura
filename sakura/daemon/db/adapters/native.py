
class NativeDatastoreAdapter:
    NAME = 'native'
    @staticmethod
    def adapt(ds):
        return ds

ADAPTER = NativeDatastoreAdapter

