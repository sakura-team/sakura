from random import getrandbits
# uniquely identify this process among all sakura processes
# in the network (os.getpid() might generate duplicate values
# since processes are running on different machines).
ORIGIN_ID = getrandbits(32)
