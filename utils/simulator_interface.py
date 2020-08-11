import re
import optparse
import sys
import socket
import time

import socketserver, threading, time

main_thread = None
server = dict()
server_thread = dict()

_numAgents = None
_base_inport = 12220
_covmaps=dict()
_neighbours=dict()
_locs=dict()

_last_simtime_recv = None
_lock = threading.Lock()

class ThreadedUDPHandler(socketserver.BaseRequestHandler):
#    def __init__(self, request, client_address, server, agentId):
#        super().__init__(request, client_address, server)
#        self.agentId = agentId

    def handle(self):
        global _covmaps, _neighbours, _locs, _lock, _last_simtime_recv
        self.agentId = 0
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
#        print("Agent {} {}: client: {}, wrote: {}".format(self.agentId, current_thread.name, self.client_address, data))
        if len(data) == 0:
                print("Empty msg")
        else:
            # I got something
            strdata = data.decode('utf-8')
            #print(strdata)
            # get agent id
            i = strdata.find('agentId')
            j = strdata.find(',',i+1)
            agentId=int(strdata[i:j].split()[1])
            #print("AgentId: ", agentId)

            #print(strdata)
            if "COVERAGEMAP" in strdata:
                #print("received message")
                _lock.acquire()
                _covmaps[agentId] = parseCoverageMap(strdata)
                _lock.release()
                print("Got CoverageMap from ", agentId)
                #print("==========   COVERAGEMAP  ===========")
                # dictionary taskid -> [0,1] (1 is not completed, 0 completed; remaining work)
                #print(covmap)
                gotCov=True
            if "NEIGHBOURS" in strdata:
                #print("received message")
                _lock.acquire()
                _neighbours[agentId] = parseNeighbours(strdata)
                _lock.release()
                print("Got Neighbours from ", agentId)
                #print("==========   NEIGHBOURS  ===========")
                # dictionary: agentid -> lasttimeseen (int)
                #print(neighbours)
                gotNeighbours=True
            if "CNTCELL" in strdata:
                #print("received message")
                _lock.acquire()
                _locs[agentId] = parseLocation(strdata)
                _lock.release()
                print("Got Current Location from ", agentId)
                #print("==========   LOCATION (TASK)  ===========")
                # dictionary: agentid -> lasttimeseen (int)
                #print(taskid)
                gotCntLoc=True
            if "SIMTIME" in strdata:
                _lock.acquire()
                _last_simtime_recv = parseSimTime(strdata)
                _lock.release()
                print("Got Current Location from ", agentId)



def _init():
    global server, server_thread, _numAgents, _base_inport
    for i in range(0,_numAgents+1):
        HOST, PORT = "0.0.0.0", _base_inport + i
        server[i] = socketserver.UDPServer((HOST, PORT), ThreadedUDPHandler)
        server_thread[i] = threading.Thread(target=server[i].serve_forever)
        server_thread[i].daemon = True
        server_thread[i].start()
        print("Server started at {} port {}".format(HOST, PORT))
    try:
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down servers ...")
        for i in range(0,_numAgents+1):
            server[i].shutdown()
            server[i].server_close()
            server_thread[i].join()



def initSimulatorInterface(numAgents, base_inport=12220):
    global main_thread, _numAgents, _base_inport
    _numAgents = numAgents
    _base_inport = base_inport

    try:
        main_thread = threading.Thread(target=_init)
        main_thread.start()
    except:
        print("Simulator Interface exited")


def parseSimTime(strtime):
    i = strtime.find("simtime")
    if i==-1:
        return None
    str1 = strtime[i:]
    j = str1.find(',')
    str1 = str1[:j]
    #print(str1)
    s = str1.split()
    #print(s)
    if len(s) != 2:
        return None
    return int(s[1])



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
    return getSimulationTime()


def getResponseFromAgent(agentId):
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

#    sendAdvanceSimTime(1)
    time.sleep(1)

    #for i in range(1,nAgents+1):
    #    sendInfoRequestToAgent(i)
    #    cmap, neigh, loc = getResponseFromAgent(i)
    #    covmaps[i] =  cmap
    #    neighbours[i] = neigh
    #    locs[i] = loc
    return _covmaps.copy(), _neighbours.copy(), _locs.copy()

def getGlobalCoverage():
    # send requests
    sendInfoRequestToAgent(0)
        # advance time ( 1 seconds should be fine)
        # remember to update time in your code

#    sendAdvanceSimTime(1)
    time.sleep(1)

    #for i in range(1,nAgents+1):
    #    sendInfoRequestToAgent(i)
    #    cmap, neigh, loc = getResponseFromAgent(i)
    #    covmaps[i] =  cmap
    #    neighbours[i] = neigh
    #    locs[i] = loc
    return _covmaps[0].copy()

def getSimulationTime():
    # request simulation time
    # send a message "SIM CTRL_REQUEST_TIME " to the UDP port number of agent 0
    # default: 12345
    global _last_simtime_recv
    # clear the last time recv
    _last_simtime_recv = None
    socketout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('localhost', 12345)
    message = "SIM CTRL_REQUEST_TIME"
    try:
        # Send data
        print('sending "%s"' % message)
        sent = socketout.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)
    # some sleep, to be safe
    time.sleep(1)
    return _last_simtime_recv
