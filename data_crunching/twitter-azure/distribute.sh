#!/bin/bash

usage="sh distribute.sh [-h] [-r | -l | -e command | -scp file] [-a | machine-nr]

where:
    -h           help
    -r           send your public key to machine
    -l           login via ssh
    -e           execute command
    -a           all machines (useful for installing stuff)
    -scp         send a file to home dir

    machine-nr   machine number 1-8
    command      command to execute remotely"

m[0]='humaniac@humanitas1.cloudapp.net'
m[1]='josephboyd@humanitas2.cloudapp.net'
m[2]='humanitas3@humanitas3.cloudapp.net'
m[3]='humaniac@humanitas4.cloudapp.net'
m[4]='h5@humanitas5.cloudapp.net'
m[5]='humaniac@humanitas6.cloudapp.net'
m[6]='humaniac@humanitas7.cloudapp.net'
m[7]='fabbrix@humanitas8.cloudapp.net'

if [ "$1" == "-h" ]; then
    echo "Usage: $usage"
    exit 0
fi

cmd="ssh"
remote_cmd=""

if [ "$1" == "-r" ]; then
    cmd="ssh-copy-id"
    machine=$2
elif [ "$1" == "-l" ]; then
    machine=$2
elif [ "$1" == "-e" ]; then
    remote_cmd=$2
    machine=$3
elif [ "$1" == "-scp" ]; then
    if [ "$3" == "-a" ]; then
        for host in ${m[@]}
        do
            echo "$host:"
            scp $2 "$host:"
        done
    else
        scp $2 "${m[$3 - 1]}:"
    fi
    exit 0
fi

if [ "$machine" == "-a" ]; then
    for host in ${m[@]}
    do
        echo "$host:"
        $cmd $host $remote_cmd
    done
else
    $cmd ${m[$machine - 1]} $remote_cmd
fi



