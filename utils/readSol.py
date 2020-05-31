import re
import optparse
import sys


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


if __name__ == "__main__":
    parser = optparse.OptionParser(usage="usage: %prog [options] filename",
                                   version="%prog 1.0")
    parser.add_option("--nice",
                      action="store_true",
                      help="show plans for agents")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        print("mandatory arguments missing (scenario)")
        parser.print_help()
        raise SystemExit

    yts = ReadSol(args[0])
    agents=list(yts.items())
    agents.sort()
    if options.nice:
        for (a, yts) in agents:
            cloc=None
            print("[",a,"]",end="")
            for (t,loc) in yts.items():
                if cloc and cloc != loc:
                    print(" ->",end="")
                cloc = loc
                print(" (",loc,")",end="")
            print("")
