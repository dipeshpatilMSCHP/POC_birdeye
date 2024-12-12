#!/bin/bash

if [ "$#" -gt 3 ]; then 
    echo "Usage: <file to compile> <output_file>"
    exit 1
fi 

arg1=$1
arg2=$2


if [ "$#" -lt 2 ]; then 
    g++ $arg1 $(pkg-config --cflags --libs opencv4) -g -o ./exes/a.out
else
    g++ $arg1 $(pkg-config --cflags --libs opencv4) -g -o $arg2
fi