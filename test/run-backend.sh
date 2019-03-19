#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/tmp.XXXXXXXX)
export PYTHONUNBUFFERED=1

MAIN_PID=$$
args="$@"

ignore_ctrl_c()
{
    trap "echo -n" SIGINT
}

on_ctrl_c()
{
    wait
    exit
}

trap "on_ctrl_c" SIGINT

prefix_out()
{
    {
        ignore_ctrl_c
        echo "$*"
        label="$1"
        shift
        "$@" 2>&1 | {
            ignore_ctrl_c
            while read line
            do
                echo "$label: $line"
            done
        }
        terminate
    } &
}

terminate()
{
    # this will signal all processes of process group
    # in the case of the main process, it will call on_ctrl_c()
    kill -INT -$MAIN_PID
    wait
}

# run the commands in the background and prefix their
# output.
prefix_out HUB test/run-hub.sh $args
sleep 3
prefix_out DAEMON0 test/run-daemon.sh 0
sleep 0.2
prefix_out DAEMON1 test/run-daemon.sh 1
sleep 0.2
prefix_out DAEMON2 test/run-daemon.sh 2

# wait for sub processes
wait
