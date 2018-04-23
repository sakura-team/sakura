class DataflowMixin:
    @classmethod
    def create_or_update(cls, dataflow_id, **kwargs):
        dataflow = cls.get(id = dataflow_id)
        if dataflow is None:
            dataflow = cls(id = dataflow_id, **kwargs)
        else:
            dataflow.set(**kwargs)
        return dataflow
    @classmethod
    def get_gui_data(cls, dataflow_id):
        dataflow = cls.get(id = dataflow_id)
        if dataflow == None:
            return None
        return dataflow.gui_data
    @classmethod
    def set_gui_data(cls, dataflow_id, gui_data):
        cls.create_or_update(dataflow_id, gui_data = gui_data)
