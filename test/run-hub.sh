#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/hub.XXXXXXXX)

WEBAPP="workflow"
if [ "$1" != "" ]
then
    WEBAPP="$1"
fi

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
        "external-datasets": [ ],
        "work-dir": "$HOME/.sakura"
    }
EOF

./hub.py -f $TMPDIR/hub.conf $WEBAPP

