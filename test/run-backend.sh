#!/bin/bash

cd $(dirname $0)/..
TMPDIR=$(mktemp -d /tmp/tmp.XXXXXXXX)
export PYTHONUNBUFFERED=1

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

on_ctrl_c()
{
    terminate
}

trap on_ctrl_c SIGINT

terminate_children()
{
    parent=$1
    for child in $(pgrep --parent $parent)
    do
        terminate_children $child
        kill $child 2>/dev/null && wait $child 2>/dev/null
    done
}

terminate()
{
    terminate_children $$
    kill $$
}

ensure_all_subprocesses_ok()
{
    ok=1
    # check
    for pid in $*
    do
        kill -0 $pid 2>/dev/null || ok=0
    done
    if [ $ok -eq 0 ]
    then
        terminate
    fi
}

# run the commands in the background and prefix their
# output.
prefix_out HUB test/run-hub.sh $args &
children=$!
sleep 3
ensure_all_subprocesses_ok $children
prefix_out DAEMON0 test/run-daemon.sh 0 datasample spacetime &
children="$children $!"
sleep 0.2
ensure_all_subprocesses_ok $children
prefix_out DAEMON1 test/run-daemon.sh 1 mean map &
children="$children $!"
sleep 0.2
ensure_all_subprocesses_ok $children
prefix_out DAEMON2 test/run-daemon.sh 2 rscript &
children="$children $!"

# wait for 1 background process to complete
wait -n
terminate
