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

'''
OUTPUT1_COLUMNS = (
    ("timestamp", int), ("tweet_id", float) , ("user_id", int), ("lang_id", str), ("longitude", float), ("latitude", float), ("text", str))

OUTPUT1 = (
    (1412771963, 5.19829E+17, 1728453457,"null","-65.215037","-26.838123","@manzurit jajjajjajajajajjajajajaaja manzur queridoooo"),
    (1412773071, 5.19834E+17, 765077353,"null","102.283834","6.036455","too ugly to be someone favourite uhuk uhuk"),
    (1412773071, 5.19834E+17,12006874,"null","141.358453","43.049568","情報過多社会だからこそ、本物の情報を取りに行かないと、情報に振り回される。"),
    (1412773071, 5.19834E+17,609041070,"null","-1.937264","43.312536","@Sr_iManoL y yo comiendo alubias. Me indigno."),
    (1412773071, 5.19834E+17,87077483,"null","125.642626","7.119793","http://t.co/tMG7oZWGih"),
    (1412773071, 5.19834E+17,131094610,"null","120.988059","14.457892","@ShaneeeMalate @mendozanelle @ravirob30 hahaha. gulo ito! jk"),
    (1412773071, 5.19834E+17,458358764,"null","8.016976","50.789111","Schlampen Shirts :D wird ja immer Besser :'D"),
    (1412773071, 5.19834E+17,280033281,"null","-2.288614","53.486064","If a boy is living off his father, he's broke. You that's living off your boyfriend...you're rich..aii?"),
    (1412773071, 5.19834E+17,569397656,"null","27.408424","37.760494","Adam evladına yardim edip duru tekmeyi evladindan yiyo anlamadim birader ben bu işi :Dasdadasada"),
    (1412773071, 5.19834E+17,237333511,"null","99.954243","12.557314","อิดอกทองส์55555555555555555555555555555555555``@faiizbnx: @snw_bana แม่ค้าอย่าเพิ่งรำคาญเลาน้าาาาาาาาาา 👉👈''"),
    (1412773071, 5.19834E+17,433148776,"null","129.744283","62.04635","@milenavonavi ну ты же сзади любишь 😹"),
    (1412773071, 5.19834E+17,199321644,"null","-46.71424","-23.491484","Ou algo assim"),
    (1412773071, 5.19834E+17,128763683,"null","101.709408","3.099425","Sketch By @encikmimpi huahahaha!!! lu mmg lejen bro!!! sketch ni mcm menganjing gua pon ada gak ni kah… http://t.co/TPJ6WI2RxD"),
    (1412773071, 5.19834E+17,261529647,"null","-58.184889","-34.80463","Que calor x dios"),
    (1412773071, 5.19834E+17,213780773,"null","28.95685","41.043714","Yorucu geçen spor v")
)
'''


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
    
