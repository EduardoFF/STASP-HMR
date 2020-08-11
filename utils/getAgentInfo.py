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
        print("mandatory arguments missing (number of agents)")
        parser.print_help()
        raise SystemExit

    numberOfAgents = int(args[0])
    # start simulator interface
    initSimulatorInterface(numberOfAgents)


    while True:
        c = input()
        if c == 'Q' or c == 'q':
            break

        # requesting coverage map and neighbours
        if c == 'R' or c == 'r':
            # get all info
            # each var is a dict agentid -> data
            covmaps, neighbours, locs = getInfo(numberOfAgents)

            # print info
            for i in locs.keys():
                print("===== Agent {} ======".format(i))
                print("Current Location: {}".format(locs[i]))
                print("Current Neighbours: ", end="")
                for (n,t) in neighbours[i].items():
                    print("Agent {} lastTimeSeen {}".format(n,t), end=" ")
                print("")
                print("Current CoverageMap: ")
                k = covmaps[i].keys()
                k=sorted(list(k))
                for taskid in k:
                    print("\t{}\t{}".format(taskid,covmaps[i][taskid]))
                print("")

        if c == 'T' or c == 't':
            print("Current time: ", getSimulationTime())

        if c == 'S' or c == 's':
            newtime = sendAdvanceSimTime(10)
            print("Simulating 10 seconds, new time is: ", newtime)

        # requesting coverage map and neighbours
        if c == 'G' or c == 'g':
            # get all info
            # each var is a dict agentid -> data
            covmap = getGlobalCoverage()

            # print info
            tasks = list(covmap.keys())
            tasks.sort()
            print("Global CoverageMap: ")
            for taskid in tasks:
                print("\t{}\t{}".format(taskid,covmap[taskid]))
                print("")




    print("Done")
