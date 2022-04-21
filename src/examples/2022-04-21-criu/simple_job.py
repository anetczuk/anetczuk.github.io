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

