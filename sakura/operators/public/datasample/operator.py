#!/usr/bin/env python
import random
from sakura.daemon.processing.operator import Operator

# info about output1
OUTPUT1_COLUMNS = (
    ("Name", str), ("Age", int),  ("Gender", str), ("Height", int))
OUTPUT1 = (
    ("John", 52, "male", 175),
    ("Alice", 34, "female", 184),
    ("Bob", 31, "male", 156),
    ("Jane", 38, "female", 164)
)

SAMPLE_POINTS = [   [31.165342,30.010138],
                    [-70.693406,19.46907],
                    [-63.8533,10.95622],
                    [103.31764,3.864095],
                    [112.745337,-7.277814],
                    [-51.225596,-30.040125],
                    [40.223849,37.919347],
                    [-98.190736,19.039094],
                    [139.638216,35.549026],
                    [-46.684644,-23.564315] ]

# info about output2
OUTPUT2_LENGTH = 1000
tmp = []
for row in range(OUTPUT2_LENGTH):
    tmp.append((random.randint(0, 1000),))
OUTPUT2 = tuple(tmp)

# info about output3 (length is not fixed)
OUTPUT3_LENGTH = random.randint(100, 200)
            
class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]
    def construct(self):
        # no inputs
        pass
        # outputs:
        # - output1: dump of OUTPUT1 (see above)
        # - output2: dump of OUTPUT2 (randomly generated integers)
        # - output3: generate OUTPUT2_LENGTH random integers
        # - output4: locations with longitude and latitudes
        output1 = self.register_output('People', self.compute1)
        output1.length = len(OUTPUT1)
        for colname, coltype in OUTPUT1_COLUMNS:
            output1.add_column(colname, coltype)
        
        output2 = self.register_output('1000 integers', self.compute2)
        output2.length = OUTPUT2_LENGTH
        output2.add_column('Integers', int)
        
        output3 = self.register_output('Random integers', self.compute3)
        output3.add_column('Integers', int)
        
        output4 = self.register_output('Locations', self.compute4)
        output4.add_column('longitude', float)
        output4.add_column('latitude', float)
       
        # no parameters
        pass
    def compute1(self):
        for row in OUTPUT1:
            yield row
    
    def compute2(self):
        for row in OUTPUT2:
            yield row
    
    def compute3(self):
        for row_idx in range(OUTPUT3_LENGTH):
            yield (random.randint(0, 1000),)
    
    def compute4(self):
        for row in SAMPLE_POINTS:
            yield row
    
