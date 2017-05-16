#Code started by Michael Ortega for the LIG
#Started on: May the 15th, 2017

#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
 
import subprocess

class Rscript(Operator):
    NAME = "Rscript"
    SHORT_DESC = "Apply R scripts."
    TAGS = [ "statistics", "R"]
    def construct(self):
        
        # input
        self.input = self.register_input('Input Table')
        
        # additional tab
        self.register_tab('Script', 'rscript.html')
                
    def compute(self):
        pass
    
    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'script':
            
            f = open('data.csv', 'w')
            for inp in self.input:
                for i in range(len(inp)-1):
                    f.write(str(inp[i])+',')
                f.write(str(inp[-1])+'\n')
            f.close()
            
            f = open('script.r', 'w')
            f.write('input_table <- read.csv("data.csv", header = FALSE, sep = ",");\n')
            f.write(event[1])
            f.close()
            
            result = str(subprocess.check_output(['Rscript','script.r']).decode("utf-8"))
            return { 'result':  result}
