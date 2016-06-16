import Orange, OWGUI, sys

from OWWidget import OWWidget
from Orange.data.PantedaConnection import PantedaConnection
from Orange.data.DelayedResultTable import DelayedResultTable

from remote_pdb import RemotePdb

TYPE_TO_FEATURE = {
    'int': Orange.feature.Continuous,
    'float': Orange.feature.Continuous,
    'str': Orange.feature.String
}

def create_orange_domain(output_desc):
    features = [ TYPE_TO_FEATURE[t](label) \
            for label, t in output_desc ]
    return Orange.data.Domain(features)

class OWPantedaOperator(OWWidget):
    def __init__(self, ui_opname, server_opname, inputs, outputs,
                        gui, parent, signalManager):
        OWWidget.__init__(self, parent, signalManager)
        
        self.ui_opname = ui_opname
        # replace each input callback name by the real callback attribute
        self.inputs = [
            (label, t, getattr(self, method_name))
            for label, t, method_name in inputs
        ]
        self.outputs = outputs
        self.received_inputs = [None] * len(inputs)
        self.server = PantedaConnection.get()
        self.op_id = self.server.register_operator(server_opname)
        
        OWGUI.button(self.controlArea, self, 'Apply', callback=self.process)
        #self.gui = gui
        #self.gui.load(self.controlArea)
    
    def set_one_input(self, i, data):
        
        #sys.stderr.write('set_one_input!! ' + repr((i, data)))
        self.received_inputs[i] = data
        # Orange calls us with input data. This means that
        # all our inputs where linked with a previous operator.
        # We consider that we are only working with operators of this
        # kind (OWPantedaOperator). Thus these source operators have sent
        # a DelayedResultTable as output (that's also what this object
        # will do below).
        # We look for the "op" attribute of these objects, and we
        # are able to send to the server information about our source
        # operators. 
        if not None in self.received_inputs:
            source_op_ids = []
            for result_table in self.received_inputs:
                source_op_ids.append(result_table.op.op_id)
            self.server.set_operator_sources(self.op_id, source_op_ids)
            self.process()

    def process(self):
        #server.set_parameters(self.op_id, self.gui.get_parameters())
        # The output we send is a "virtual" result table whose entries
        # will be computed on the fly when needed.
        #sys.stderr.write('OWPantedaOperator.process... ' + repr(self) + '\n')
        #sys.stderr.write(repr(self.inputs) + '\n')
        
        #RemotePdb('127.0.0.1', 4444).set_trace()
        
        # if all entries were given
        if not None in self.received_inputs:
            ########
            #!!!!!!!!!!TODO: GERER PLUSIEURS TABLES EN SORTIE
            ########
            domain = create_orange_domain(
                  self.server.describe_outputs(self.op_id)[0])
            res = DelayedResultTable(self, domain)
            sys.stderr.write('** DEBUG %s - results:\n' % self.ui_opname)
            for i in res:
                sys.stderr.write(repr(i) + '\n')
            sys.stderr.write('\n')
            self.send(self.outputs[0][0], res)
            
            #self.gui.set_result_table(res)

    def __iter__(self):
        return self.server.get_operator_iterator(self.op_id)

    def get_output_len(self):
        return self.server.get_operator_output_len(self.op_id)

    def get_output(self, i):
        return self.server.get_operator_output(self.op_id, i)
        
    @staticmethod
    def createInputMethods(num):
        # we dynamically create a callback called "set_input_<i>"
        # for each input.
        method_names = []
        method_funcs = []
        for i in range(num):
            def set_input_i(obj, data):
                obj.set_one_input(i, data)
            method_names += [ 'set_input_' + str(i) ]
            method_funcs += [ set_input_i ]
        return method_names, method_funcs
        
    @staticmethod
    def createOperatorSubClass(module, server_opname, method_names, method_funcs):
        # create operator __init__() function
        def __init__(self, parent=None, signalManager=None):
            OWPantedaOperator.__init__(self,
                ui_opname = module.NAME,
                server_opname = server_opname,
                inputs = module.INPUTS,
                outputs = module.OUTPUTS,
                gui = None,
                parent = parent, 
                signalManager = signalManager)

        # operator methods are the input methods plus the __init__
        op_class_methods = { name: func for name, func in \
                                zip(method_names, method_funcs) }
        op_class_methods["__init__"] = __init__

        # compute a class name
        op_class_name = 'OWUT' + module.NAME
            
        # dynamically create the subclass of OWPantedaOperator
        op_class = type(
            op_class_name,              # class name
            (OWPantedaOperator,),       # base classes
            op_class_methods            # members
        )
        return op_class_name, op_class

    @staticmethod
    def setupOperatorModule(module_name, server_opname, inputs, outputs, **kwargs):
        #RemotePdb('127.0.0.1', 4444).set_trace()
        # sanitize parameters
        if not inputs:
            inputs = []
        if not outputs:
            outputs = []
        # retrieve caller module name
        mod = sys.modules[module_name]
        # copy named args as module attributes
        for key, value in kwargs.items():
            setattr(mod, key, value)
        # compute OUTPUTS
        mod.OUTPUTS = [(label, DelayedResultTable) for label in outputs]
        # prepare input methods
        method_names, method_funcs = OWPantedaOperator.createInputMethods(len(inputs))
        # compute INPUTS
        mod.INPUTS = [ (label, DelayedResultTable, method_name) \
                                for label, method_name in \
                                zip(inputs, method_names) ]

        # compute the operator subclass and register it in the module
        op_class_name, op_class = OWPantedaOperator.createOperatorSubClass(
                mod, server_opname, method_names, method_funcs)
        setattr(mod, op_class_name, op_class)

