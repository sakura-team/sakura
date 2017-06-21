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
    # Delete all operators created for Tweetsmap 
    rm -rf $HOME/.sakuraTweetsmap
    echo "Deleted Tweetsmap operators"
}

# whatever happens, call on_exit() at the end.
trap on_exit EXIT

# prepare hub conf
if [ "$1" == "" ]
then
cat > $TMPDIR/hub.conf << EOF
    {
        "web-port": 8081,
        "hub-port": 10432,
        "external-datasets": [ ],
        "work-dir": "$HOME/.sakura"
    }
EOF
else
cat > $TMPDIR/hub.conf << EOF
    {
    "web-port": 8080,
    "hub-port": 10432,
    "external-datasets":[],
    "work-dir": "$HOME/.sakuraTweetsmap"
    }
EOF
fi

./hub.py -f $TMPDIR/hub.conf $WEBAPP

