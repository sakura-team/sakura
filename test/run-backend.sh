#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/tmp.XXXXXXXX)

prefix_out()
{
    echo "$*"
    label="$1"
    shift
    "$@" 2>&1 | while read line
    do
        echo "$label: $line"
    done
}

on_exit()
{
    # in case of ctrl-c, the wait at the end of the script
    # is cancelled, thus we get here, and the background
    # processes receive SIGINT.

    # we wait again to make sure the background processes
    # have completed there cleanup procedure and exited.
    wait
    #rm -rf $TMPDIR
}

# whatever happens, call at_exit() at the end.
trap on_exit EXIT

# prepare hub conf
mkdir -p $TMPDIR/hub
cat > $TMPDIR/hub/hub.conf << EOF
{
    "web-port": 8081,
    "hub-port": 10432,
    "external-datasets": [ ]
}
EOF

# prepare daemon0 and daemon1 conf and operators
mkdir -p $TMPDIR/daemon0/operators $TMPDIR/daemon1/operators
cp -r sakura/operators/public/datasample $TMPDIR/daemon0/operators
cp -r sakura/operators/public/mean $TMPDIR/daemon1/operators
for i in 0 1
do
    cat > $TMPDIR/daemon$i/daemon.conf << EOF
{
    "hub-host": "localhost",
    "hub-port": 10432,
    "daemon-desc": "daemon $i",
    "operators-dir": "$TMPDIR/daemon$i/operators",
    "external-datasets": [ ]
}
EOF
done

# run the commands in the background and prefix their
# output.
prefix_out HUB ./hub.py -f $TMPDIR/hub/hub.conf workflow &
sleep 1
for i in 0 1
do
    prefix_out DAEMON$i ./daemon.py -f $TMPDIR/daemon$i/daemon.conf &
done

# wait for background processes to complete
wait

