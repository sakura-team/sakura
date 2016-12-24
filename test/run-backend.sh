#!/bin/bash

cd $(dirname $0)/..

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

# whatever happens, call at_exit() at the end.
trap on_exit EXIT

# run the commands in the background and prefix their
# output.
prefix_out HUB ./hub.py workflow &
sleep 0.1
prefix_out DAEMON ./daemon.py -f test/conf/daemon.conf &

# wait for background processes to complete
wait

