import sys
# if started interactive, first element is ''
# if in a script, first element is the directory
# of the script.
# to avoid conflicts in module name (e.g. importing
# collections.operator could import local operator.py
# instead), we want to favor names of the standard
# library. Thus we move this directory at the end
# of the list.
if sys.path[0] != '':
    sys.path = sys.path[1:] + [ sys.path[0] ]
