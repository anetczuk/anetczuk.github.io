---
title: Dumping and restoring Unix processes

summary: Basic use case of CRIU tool.
---

Let's say there is application with complex internal state. Let's say there is a 
need to persist it's state for further use. One way to solve the problem would be 
to dump the state programically from within the application. In *Python* problem 
could be solved for example using ```pickle```. Unfortunately *C++* users have no 
luck. Moreover, in *C++* it's not always possible to access internal state of application. 
Cases include accessing internals of linked libraries (e.g. of RNG from ```cstdlib```).

Other possible solution for the problem is to dump application's whole memory and 
restore it later using capabilities of operating system. One such tool is *CRIU*. 

CRIU provides two basic operations: *dump* and *restore* alowing to persisting and 
loading processes respectively. For dumping it takes two additional parameters: PID 
of the process to persist and directory to store the state. Restore needs directory 
where *dump* operation saved the state.


### Simple example

Take look at following *simple_job.py* program:
```
#!/usr/bin/env python3

###
### Infinitely print random number every 2 seconds.
###

import os
import time
import random


pid = os.getpid()
print( "PID:", pid )


counter = 0

while True:
    counter += 1
    rnum = random.randrange( 999999 )
    print( pid, "step:", counter, "rand:", rnum )
    time.sleep( 2.0 )
```
Program just prints random number in interval of 2 seconds.


Simple dump script *dump.sh* could look like:
```
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

```
Script looks for PID of process by it's executable name, then takes it and dumps 
the process.

Corresponding restore script *restore.sh*:
```
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

```
It opens storage directory and restores dumped process.

Given CRIU scripts use additional parameters to control CRIU:

- ```--shell-job``` -- allow to dump/restore processes started from command line
- ```-R``` -- do not terminate the process during dump step


Restore script can be run more than once (sequentailly). Output of restored process 
will always be the same -- copy of restored process will always generate the same 
random numbers.


### Limitations

CRIU works locally and as primary operation stores content of *RAM* memory of given 
process. Consequently it is not capable of persisting external resources such as 
content of local files or connected components. 

Detailed list of limitations can be found [here](https://criu.org/What_cannot_be_checkpointed).


## References

- [CRIU main page](https://criu.org/Main_Page)
- [CRIU limitations](https://criu.org/What_cannot_be_checkpointed)
