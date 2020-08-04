import re
import optparse
import sys
import socket
import time


# reads a .sol file to retrieve the tasks
def ReadSol(fname):
    loc_t = {}
    loc_w = {}
    loc_yt = {}
    myregexW = re.compile('W\[(\d+),(\d+)\]')
    myregexT = re.compile('T\[(\d+),(\d+)\]')
    p_d = {}
    s_d = {}
    f = open(fname)
    for line in f.readlines():
        s = line.split()
        if len(s):
            tok = s[0]
            if tok[0] == 'T':
                pns = myregexT.findall(tok)
                #print pns
                t = int(s[1])
                if len(pns) == 1:
                    (k,l) = pns[0]
                    #k=int(k)
                    #l=int(l)
                    loc_t[k,t] = l
                    #print k,l,t,d
            if tok[0] == 'W':
                pns = myregexW.findall(tok)
                w = int(s[1])
                if len(pns) == 1:
                    (k,l) = pns[0]
                    #k=int(k)
                    #l=int(l)
                    loc_w[k,l] = w
    #print loc_w
    #print loc_t
    A = [a for (a,l) in loc_w.keys()]
    A = set(A)
    #print A

    yts = {}
    for a in A:
        ct = 1
        yta = dict()
        while True:
            #print "a",a,"ct",ct,
            if not loc_t.get((a,ct)):
                break
            l = loc_t[(a,ct)]
            #print "loc",l
            if not loc_w.get((a,l)):
                break
            wl = loc_w[(a,l)]
            for t in range(ct,ct+wl):
                yta[t] = l
            ct = ct+wl
        yts[a] = yta
    return yts

""" sends a task to the simulator """
def sendTaskByUDP(socket, server_addr, agentid, seqno, start, end, loc):
    message = "TASK {} {} {} {} {}".format(agentid, seqno, start, end, loc)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = sock.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)

""" sends UDP message to advance simulator t seconds """
def sendAdvanceSimTime(sock, server_addr, t):
    message = "SIM CTRL_ADVANCE_TIME {}".format(t)
    try:
        # Send data
        print('sending "%s"' % message)
        sent = sock.sendto(bytes(message, 'UTF-8'), server_addr)
    except Exception as e:
        print("Error while sending ", e)


if __name__ == "__main__":
    parser = optparse.OptionParser(usage="usage: %prog [options] filename",
                                   version="%prog 1.0")

    parser.add_option("--run",
                      action="store_true",
                      help="advance time in simulator")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        print("mandatory arguments missing (scenario)")
        parser.print_help()
        raise SystemExit

    yts = ReadSol(args[0])
    agents=list(yts.items())

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    agents.sort()
    maxtime = 0  # to keep track of the makespan (end of the mission)
    for (a, yts) in agents:
        # yts is a map from timestep to task
        print("[",a,"]",end="")
        # the simulator is listen to a different port for each agent
        # port are 12345 + (agentid)
        server_address = ('localhost', 12345+int(a))
        for (t,loc) in yts.items():
            print(t, " ", loc)
            # t is the timestep, we should multiply by 300
            maxtime = max(maxtime, t)
            # task at time t means from time ((t-1)*300 + 1) to time t*300
            # t goes from 1
            sendTaskByUDP(sock, server_address, a, t, (t-1)*300 + 1, t*300, loc )
            # some pause to avoid buffer overflow
            time.sleep(0.001)
        print("")
    print("MAXTIME = ", maxtime)
    # send the SIM CTRL_ADVANCE_TIME to port 12345
    if options.run:
        server_address = ('localhost', 12345)
        sendAdvanceSimTime(sock, server_address, (maxtime+1)*300)

    sock.close()
