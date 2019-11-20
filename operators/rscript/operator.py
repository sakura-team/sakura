#Code started by Michael Ortega for the LIG
#Started on: May the 15th, 2017

#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator

import os

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
    
    def handle_event(self, ev_type, source_code):
        if ev_type == 'script':
            
            f = open('data.csv', 'w')
            for inp in self.input:
                for i in range(len(inp)-1):
                    f.write(str(inp[i])+',')
                f.write(str(inp[-1])+'\n')
            f.close()
            
            f = open('script.r', 'w')
            f.write('input_table <- read.csv("data.csv", header = FALSE, sep = ",");\n')
            f.write(source_code)
            f.close()
            
            os.system('Rscript script.r > rscript.out 2> rscript.err')
            return {    'out': open('rscript.out', 'r').read(), 
                        'err': open('rscript.err', 'r').read()  }
