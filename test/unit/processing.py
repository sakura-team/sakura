#!/usr/bin/env python3
import os, sys
os.environ['UNIT_TEST'] = 'yes'
sys.path.insert(0, '.')
from sakura.operators.datasample.operator import DataSampleOperator
from sakura.operators.mean.operator import MeanOperator

print("""
Expected results:
---
[(1, 'Age (of Input table)'), (3, 'Height (of Input table)')]
(169.75,)

Running test:
---\
""")

op0 = DataSampleOperator()
op0.construct()
op1 = MeanOperator()
op1.construct()
op1.input_tables[0].connect(op0.output_tables[0])
print(op1.parameters[0].get_possible_values())
op1.parameters[0].select(3)
op1.is_ready()
for row in op1.output_tables[0]:
    print(row)

