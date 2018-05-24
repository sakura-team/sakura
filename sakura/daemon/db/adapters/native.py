
class NativeDatastoreAdapter:
    NAME = 'native'
    @staticmethod
    def adapt(engine, ds):
        return ds

ADAPTER = NativeDatastoreAdapter

