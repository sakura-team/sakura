from sakura.daemon.processing.operator import Operator

class SortOperator(Operator):
    NAME = "Sort"
    SHORT_DESC = "Sort operator."
    TAGS = [ "sort" ]
    def construct(self):
        # inputs
        self.input_plug = self.register_input('Input data')
        # outputs
        self.output_plug = self.register_output('Sorted data')
        # parameters
        self.column_param = self.register_parameter(
                'ANY_COLUMN_SELECTION', 'input column', self.input_plug)
        self.column_param.on_change.subscribe(self.update_output)

    def update_output(self):
        source = self.input_plug.source
        input_column = self.column_param.column
        # apply sort
        source = source.sort(input_column)
        # update output source
        self.output_plug.source = source
