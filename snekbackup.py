#!/bin/python2.7

import sys
import subprocess


if len(sys.argv) != 3:
    print("Srsly, you need 2 arguments or it won't work.")
    print("Usage: python2.7 snekbackup.py [regex] [destination folder] ")
else:
    subprocess.call("find / -type f -name " + '"' + sys.argv[1] + '"' + " -exec cp {} " + sys.argv[2], shell=True)