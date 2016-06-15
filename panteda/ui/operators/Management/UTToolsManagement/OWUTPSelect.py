#!/usr/bin/python
#Orange Widget initiated by Etienne Duble and Michael ORTEGA - 8/06/2016

from Orange.data.OWPantedaOperator import OWPantedaOperator

OWPantedaOperator.setupOperatorModule(
    module_name = __name__,
    server_opname = 'OWPantedaSelect',
    inputs = [ "Input Table" ],
    outputs = [ 'One Column' ],
    NAME = 'PSelect',
    ICON = 'OWUTPSelect_icons/OWUTPSelect.svg',
    DESCRIPTION = 'Select one column',
    PRIORITY = 40,
)



