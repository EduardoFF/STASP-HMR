import re
import optparse
import sys
import socket
import time



def parseCoverageMap(strcovmap):
    i = strcovmap.find("COVERAGEMAP[")
    if i==-1:
        return None
    str1 = strcovmap[i:]
    i = str1.find('[')
    if i==-1:
        return None

    str1=str1[i+1:]
    j=str1.find(']')
    if j==-1:
        return None
    str1=str1[:j]

    s=str1.split()
    if len(s) == 0:
        return None
    nEntries = int(s[0])
    cmap=dict()
    for i in range(1,len(s),2):
        taskid = int(s[i])
        cov = float(s[i+1])
        cmap[taskid] = cov
    if len(cmap) != nEntries:
        print("WARNING: number of entries does not match number of tasks")

    # The data should be token 1
    return cmap


def parseNeighbours(strneigh):
    i = strneigh.find("NEIGHBOURS[")
    if i==-1:
        return None
    str1 = strneigh[i:]
    i = str1.find('[')
    if i==-1:
        return None

    str1=str1[i+1:]
    j=str1.find(']')
    if j==-1:
        return None
    str1=str1[:j]

    s=str1.split()
    if len(s) == 0:
        return None
    nEntries = int(s[0])
    nlist=dict()
    for i in range(1,len(s),2):
        agentid = int(s[i])
        lasttimeseen = int(s[i+1])
        nlist[agentid] = lasttimeseen
    if len(nlist) != nEntries:
        print("WARNING: number of entries does not match number of neighbours")

    # The data should be token 1
    return nlist


def parseLocation(strloc):
    i = strloc.find("NOTIFY_CELL[")
    if i==-1:
        return None
    str1 = strloc[i:]
    i = str1.find('[')
    if i==-1:
        return None

    str1=str1[i+1:]
    j=str1.find(']')
    if j==-1:
        return None
    str1=str1[:j]

    s=str1.split()
    if len(s) == 0:
        return None
    return int(s[3])


def sendInfoRequestToAgent(agentId):
    # request a coverage map
    # send a message "CTRL REQMAP" to the UDP port number of the agent
    # default: 12345 + agentId (port number)
    socketout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('localhost', 12345+int(agentId))
    message = "CTRL REQMAP {}".format(agentId)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = socketout.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)
    # some sleep, to be safe
    #time.sleep(0.001)

    message = "CTRL REQNEIGHBOURS {}".format(agentId)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = socketout.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)
    # some sleep, to be safe
    #time.sleep(0.001)

    message = "CTRL REQLOC {}".format(agentId)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = socketout.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)
    # some sleep, to be safe
    #time.sleep(0.001)
    socketout.close()


""" sends UDP message to advance simulator t seconds """
def sendAdvanceSimTime(t):
    socketout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('localhost', 12345)  # agent 0 (command center)

    message = "SIM CTRL_ADVANCE_TIME {}".format(t)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = socketout.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)
    # some sleep, to be safe
    #time.sleep(0.001)
    socketout.close()


def getResponseFromAgent(agentId, base_inport=12220):
    udpInPort = base_inport + agentId
    socketin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketin.bind(("0.0.0.0", udpInPort))
    print("waiting response from agent ", agentId, " in port ", udpInPort)
    socketin.settimeout(2)  # time out two seconds


    gotCov=False
    gotNeighbours=False
    gotCntLoc=False

    # return values, initially None
    covmap=None
    neighbours=None
    taskid=None
    while not gotCov or not gotNeighbours or not gotCntLoc:
        try:
            data, addr = socketin.recvfrom(8000) # buffer size is 8000 bytes
        except socket.timeout as  e:
            err = e.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 'timed out':
                time.sleep(1)
                print('recv timed out, retry later')
                continue
            else:
                print("Error while recv")
                print(e)
                break
        except socket.error as e:
            # Something else happened, handle error, exit, etc.
            print("Error while recv")
            print(e)
            break
        else:
            if len(data) == 0:
                print("Empty msg")
                break
            else:
                # I got something
                strdata = data.decode('utf-8')
                #print(strdata)
                if "COVERAGEMAP" in strdata:
                    #print("received message")
                    covmap = parseCoverageMap(strdata)
                    #print("==========   COVERAGEMAP  ===========")
                    # dictionary taskid -> [0,1] (1 is not completed, 0 completed; remaining work)
                    #print(covmap)
                    gotCov=True
                if "NEIGHBOURS" in strdata:
                    #print("received message")
                    neighbours = parseNeighbours(strdata)
                    #print("==========   NEIGHBOURS  ===========")
                    # dictionary: agentid -> lasttimeseen (int)
                    #print(neighbours)
                    gotNeighbours=True
                if "CNTCELL" in strdata:
                    #print("received message")
                    taskid = parseLocation(strdata)
                    #print("==========   LOCATION (TASK)  ===========")
                    # dictionary: agentid -> lasttimeseen (int)
                    #print(taskid)
                    gotCntLoc=True
    socketin.close()
    return covmap, neighbours, taskid




def getInfo(nAgents):
    # send requests
    covmaps=dict()
    neighbours=dict()
    locs=dict()

    for i in range(1,nAgents+1):
        sendInfoRequestToAgent(i)
        # advance time ( 1 seconds should be fine)
        # remember to update time in your code
        sendAdvanceSimTime(1)
        cmap, neigh, loc = getResponseFromAgent(i)
        covmaps[i] =  cmap
        neighbours[i] = neigh
        locs[i] = loc
    return covmaps, neighbours, locs
