#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/hub.XXXXXXXX)
export PYTHONUNBUFFERED=1

WEBAPP="web_interface"
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

# if there is no central db yet
if [ ! -f "$HOME/.sakura/central.db" ]
then
    # and a custom db skeleton is provided
    # in the 'test' directory
    if [ -f "test/hub-central.db" ]
    then
        # copy this db skeleton
        cp "test/hub-central.db" "$HOME/.sakura/central.db"
    fi
fi

# prepare hub conf
cat > $TMPDIR/hub.conf << EOF
{
    "web-port": 8081,
    "hub-port": 10432,
    "work-dir": "$HOME/.sakura"
}
EOF

./hub.py -f $TMPDIR/hub.conf $WEBAPP

