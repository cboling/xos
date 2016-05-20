#!/usr/bin/env bash
#
# This script takes in one or more comma separated lists of nodes-names/ip-addrs and creates the appropriate
# number of docker --add-host options to use with Docker Run commands
#
if [ $# -ne 1 ]
then
    echo "Usage: $0 <hosts-string>"    >&2
    echo "  where:"    >&2
    echo ""    >&2
    echo "    host-string = host-name/host-ip[,host-name2/host-ip2[,...]]"    >&2
    echo ""    >&2
    echo "     ...Also make sure your host(s)-string does not contain spaces !"    >&2
    echo ""    >&2
    exit 1
fi
OUTPUT=""

# Split into array of host-name/host-ips

IFS=',' read -r -a host_array <<< "$1"

for host_info in "${host_array[@]}"
do
    # Split into host and IP address

    IFS='/' read -r -a node_and_ip <<< "${host_info}"

    if [ ${#node_and_ip[@]} -ne 2 ]
    then
        echo "Invalid node name/IP: '$host_info'"
        exit 2
    fi
    OUTPUT="${OUTPUT} --add-host=${node_and_ip[0]}:${node_and_ip[1]}"
done

echo ${OUTPUT}