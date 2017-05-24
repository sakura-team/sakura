#!/usr/bin/env python
from pkg_resources import resource_string
import zlib, pickle
from sakura.daemon.processing.stream import SimpleStream

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
    if data is None:
        load_data()
    for row in data.T:
        yield tuple(row)

# dataset description
STREAM = SimpleStream('GPS Data, Paris', compute)
STREAM.add_column("Longitude", float, ('longitude',))
STREAM.add_column("Latitude", float, ('latitude',))
# we consider LENGTH is unknown
