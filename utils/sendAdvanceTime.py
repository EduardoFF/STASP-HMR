import re
import optparse
import sys
import socket
import time
from simulator_interface import *


if __name__ == "__main__":
    parser = optparse.OptionParser(usage="usage: %prog [options] filename",
                                   version="%prog 1.0")


    (options, args) = parser.parse_args()
    if len(args) == 0:
        print("mandatory arguments missing (time)")
        parser.print_help()
        raise SystemExit
    t=int(args[0])
    sendAdvanceSimTime(t)
