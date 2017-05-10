#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/tmp.XXXXXXXX)

args="$@"

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
}

# whatever happens, call on_exit() at the end.
trap on_exit EXIT

# run the commands in the background and prefix their
# output.
prefix_out HUB test/run-hub.sh $args &
sleep 3
prefix_out DAEMON0 test/run-daemon.sh 0 datasample spacetime & 
sleep 0.2
prefix_out DAEMON1 test/run-daemon.sh 1 mean map &

# wait for background processes to complete
wait

