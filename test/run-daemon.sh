#!/bin/bash

daemon_index="$1"
shift
operators=$*

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/daemon$daemon_index.XXXXXXXX)
export PYTHONUNBUFFERED=1

on_exit()
{
    rm -rf $TMPDIR
}

# whatever happens, call at_exit() at the end.
trap on_exit EXIT

# prepare daemon conf and operators
mkdir -p $TMPDIR/operators
for operator in $operators
do
    ln -s $PWD/sakura/operators/public/$operator $TMPDIR/operators/$operator
done
cat > $TMPDIR/daemon.conf << EOF
{
    "hub-host": "localhost",
    "hub-port": 10432,
    "daemon-desc": "daemon $daemon_index",
    "operators-dir": "$TMPDIR/operators",
    "data-stores": [ ]
}
EOF
# Sample data-store configuration:
#   [...]
#   "data-stores": [
#       {
#           "host": "<dbms-ip-or-hostname>",
#           "admin-user": "<dbms-admin-user>",
#           "admin-password": "<dbms-admin-password>",
#           "driver": "postgresql"
#       }
#   ]
#   [...]

./daemon.py -f $TMPDIR/daemon.conf

