#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/hub.XXXXXXXX)

on_exit()
{
    rm -rf $TMPDIR
}

# whatever happens, call on_exit() at the end.
trap on_exit EXIT

# prepare hub conf
cat > $TMPDIR/hub.conf << EOF
{
    "web-port": 8081,
    "hub-port": 10432,
    "external-datasets": [ ]
}
EOF

./hub.py -f $TMPDIR/hub.conf web_interface

