#!/bin/bash

set -eu

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


##
## check root privilege
##
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


##
## restore process
##
dump_dir="$SCRIPT_DIR/dump/"

criu restore --shell-job -D $dump_dir


echo "Process restored from $dump_dir"

