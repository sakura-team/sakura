#!/usr/bin/env bash

rm -rf /tmp/op1
{
    echo 1  # inputs
    echo 2  # outputs
    echo 2  # parameters
    echo 5  # param1
    echo 2  # param2
    echo 1  # tabs
} | ./opskeleton.py /tmp/op1 && cat /tmp/op1/operator.py
