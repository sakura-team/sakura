#!/usr/bin/python
#Orange Widget initiated by Etienne Duble and Michael ORTEGA - 8/06/2016

from Orange.data.OWPantedaOperator import OWPantedaOperator

OWPantedaOperator.setupOperatorModule(
    module_name = __name__,
    server_opname = 'OWPantedaData',
    inputs = None,
    outputs = [ 'Data' ],
    NAME = 'PData',
    ICON = 'OWUTPData_icons/OWUTPData.svg',
    DESCRIPTION = 'Generate data',
    PRIORITY = 40,
)



