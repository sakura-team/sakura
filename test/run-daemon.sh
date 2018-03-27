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

CUSTOM_DATASTORES_CONF="$PWD/test/daemon${daemon_index}-datastores.conf"
if [ -f "$CUSTOM_DATASTORES_CONF" ]
then
    DATASTORES_CONF="$(cat "$CUSTOM_DATASTORES_CONF")"
else
    DATASTORES_CONF="[ ]"
fi

cat > $TMPDIR/daemon.conf << EOF
{
    "hub-host": "localhost",
    "hub-port": 10432,
    "daemon-desc": "daemon $daemon_index",
    "operators-dir": "$TMPDIR/operators",
    "data-stores": $DATASTORES_CONF
}
EOF
# Sample data-store configuration:
#   [...]
#   "data-stores": [
#       {
#           "host": "<dbms-ip-or-hostname>",
#           "datastore-admin": {
#               "user":     "<dbms-admin-user>",
#               "password": "<dbms-admin-password>"
#           },
#           "sakura-admin": "<sakura-username>",
#           "access-scope": "<public|restricted|private>",
#           "driver": "postgresql"
#       }
#   ]
#   [...]

./daemon.py -f $TMPDIR/daemon.conf

