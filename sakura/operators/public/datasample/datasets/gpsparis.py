#!/usr/bin/env python
from pkg_resources import resource_string
import zlib, pickle

data = None

def load_data():
    global data
    print('Loading data file gpsparis.dat... ',)
    # data is compressed in file gpsparis.dat
    compressed_data = resource_string(__name__, 'gpsparis.dat')
    info = pickle.loads(zlib.decompress(compressed_data))
    data = info['data']
    data = data.astype(float) / info['factor']
    data[0] += info['offsets']['lng']
    data[1] += info['offsets']['lat']
    data = data.round(decimals=4)
    print('done.')

def compute():
    if data == None:
        load_data()
    for row in data.T:
        yield tuple(row)

# dataset description
NAME = 'GPS Data, Paris'
COLUMNS = ( ("Longitude", float, ('longitude',)),
            ("Latitude", float, ('latitude',)))
COMPUTE_CALLBACK = compute
# we consider LENGTH is unknown
