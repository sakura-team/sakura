#!/bin/bash
set -e

req()
{
    echo -n $1 "-> "
    curl http://localhost:8080$1
    echo
}

# create operators
req /operator/register/OWSakuraData    # -> op_id 0
req /operator/register/OWSakuraSelect  # -> op_id 1
req /operator/register/OWSakuraMean    # -> op_id 2

# link operators
req /link/0/0/to/1/0
req /link/1/0/to/2/0

# observe mean output
req /operator/2/outputs
req /operator/2/result/0/len
req /operator/2/result/0/row/0

# observe using iterators
req /operator/2/iterate                 # -> it_id 0
req /iterator/0/next
req /iterator/0/next

