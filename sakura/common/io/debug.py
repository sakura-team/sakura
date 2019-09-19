import io, sys

# caution:
# with DEBUG_LEVEL >= 1, some additionnal messages may be sent, in order
# to get the string representation of a remote object:
# print(<remote_obj>) will cause a request / response in order to call
# <remote_obj>.__str__().

DEBUG_LEVEL = 0   # do not print messages exchanged
#DEBUG_LEVEL = 1   # print requests and results, truncate if too verbose
#DEBUG_LEVEL = 2   # print requests and results (slowest mode)

def print_debug(*args):
    if DEBUG_LEVEL == 0:
        return  # do nothing
    OUT = io.StringIO()
    try:
        print(*args, file=OUT)
    except:
        OUT.write("<obj-to-str-exception>\n")
    if DEBUG_LEVEL == 1 and OUT.tell() > 110:
        OUT.seek(110)
        OUT.write('...\n')
        OUT.truncate()
    sys.__stdout__.write(OUT.getvalue())
