#!/usr/bin/env python
import zlib, pickle, numpy as np
from sakura.daemon.processing.source import NumpyArraySource

def load_data():
    print('Loading data file gpsparis.dat... ',)
    # data is compressed in file gpsparis.dat
    this_file_path = __module_path__
    with (this_file_path.parent / 'gpsparis.dat').open('rb') as f:
        compressed_data = f.read()
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
SOURCE = NumpyArraySource('GPS Data, Paris', load_data())
SOURCE.columns[0].add_tags('longitude')
SOURCE.columns[1].add_tags('latitude')
# we consider LENGTH is unknown
