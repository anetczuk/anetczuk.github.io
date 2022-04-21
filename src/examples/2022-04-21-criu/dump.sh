#!/bin/bash

set -eu

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


##
## find PID by process name
##
pid_list=$(pgrep -f simple_job.py)

echo -e "found PIDs:\n$pid_list"

readarray -t pid_array <<<"$pid_list"

last_pid=${pid_array[-1]}

echo "last PID: ${last_pid}"


##
## check root privilege
##
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


##
## dump process
##
dump_dir="$SCRIPT_DIR/dump/"

criu dump --shell-job -R -t ${last_pid} -D $dump_dir


echo "Dump done to $dump_dir"

