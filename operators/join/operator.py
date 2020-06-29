from sakura.daemon.processing.operator import Operator

class JoinOperator(Operator):
    NAME = "Join"
    SHORT_DESC = "Join operator."
    TAGS = [ "join" ]
    def construct(self):
        # inputs
        self.input_1 = self.register_input('Input 1')
        self.input_2 = self.register_input('Input 2')
        # outputs
        self.output = self.register_output('Joined data')
        # parameters
        self.column_param_1 = self.register_parameter(
                'NUMERIC_COLUMN_SELECTION', 'input column 1', self.input_1)
        self.column_param_1.on_change.subscribe(self.update_output)
        self.column_param_2 = self.register_parameter(
                'NUMERIC_COLUMN_SELECTION', 'input column 2', self.input_2)
        self.column_param_2.on_change.subscribe(self.update_output)

    def update_output(self):
        input_col_1 = self.column_param_1.column
        input_col_2 = self.column_param_2.column
        if input_col_1 is None or input_col_2 is None:
            self.output.source = None  # not ready yet
            return
        source_1 = self.input_1.source
        source_2 = self.input_2.source
        # apply join
        out_source = source_1.join(source_2).where(input_col_1 == input_col_2)
        # update output source
        self.output.source = out_source
