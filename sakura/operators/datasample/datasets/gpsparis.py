#!/usr/bin/env python
from pkg_resources import resource_string
import zlib, pickle, numpy as np
from sakura.daemon.processing.stream import NumpyArrayStream

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
    data = np.array(list(map(tuple, data.T)),
            [('Longitude', float),('Latitude', float)])
    print('done.')
    return data

# dataset description
STREAM = NumpyArrayStream('GPS Data, Paris', load_data())
STREAM.columns[0].add_tags('longitude')
STREAM.columns[1].add_tags('latitude')
# we consider LENGTH is unknown
