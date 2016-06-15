#!/usr/bin/python
#Orange Widget initiated by Michael ORTEGA - 20/May/2014

from Orange.data.OWPantedaOperator import OWPantedaOperator

OWPantedaOperator.setupOperatorModule(
    module_name = __name__,
    server_opname = 'OWPantedaMean',
    inputs = [ "Input Table" ],
    outputs = [ 'Mean' ],
    NAME = 'PMean',
    ICON = 'OWUTPMean_icons/OWUTPMean.svg',
    DESCRIPTION = 'mean one column',
    PRIORITY = 40,
)



