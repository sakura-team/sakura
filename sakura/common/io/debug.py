import io, sys

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
    sys.stdout.write(OUT.getvalue())
