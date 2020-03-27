import operator

def inColumnOperator(value, bbox):
    return value in bbox    # will call __contains__() method of bbox

LOWER            = operator.lt
LOWER_OR_EQUAL   = operator.le
GREATER          = operator.gt
GREATER_OR_EQUAL = operator.ge
IN               = inColumnOperator
EQUALS           = operator.eq
NOT_EQUALS       = operator.ne
