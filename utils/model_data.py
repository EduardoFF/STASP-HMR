A = []  # Set of agents
E = {}  # Adjacency set, A -> list of (i,j)
ALoc = {}  # A -> locations
ALOCS = [] # Locations
DUMMIES = ['START','END']
CELLS = []
initLoc = {}
riLoc = {}
rLoc = {}
expl = {}
ADJ = {} # Maps loc -> adjacent locs
maxTime = 0
# Read distances
d_matrix = {}
coos = {}
completeTimePerTask={}

DAPPROX_C1 = 0.4278
DAPPROX_C2 = 0.9339
EARLIESTDEP = 1
d = {}
expl_th = 0.05
reachable_demand = None
scale_factor = None
EPSILON = 1e-05
USE_COO=False

fixed_alloc = {}
forbidden_alloc = {}

def readMDATA(filename):
    global A,E,ALoc,expl,scale_factor, \
        riLoc,rLoc,maxTime,d,d_matrix,coos,USE_COO, completeTimePerTask, \
        fixed_alloc, forbidden_alloc, reachable_demand

    f = open(filename)
    lines = f.readlines()

    for line in lines:
        s = line.split()
        if( len(s)):
            if s[0] == 'AGENTS':
                for a in s[1:]:
                    A.append(a)
            if s[0] == 'CELLS':
                for c in s[1:]:
                    CELLS.append(c)
            if s[0] == 'REACHABLE_LOCS':
                locs = list()
                for l in s[2:]:
                    locs.append(l)
                ALoc[s[1]] = locs

            if s[0] == 'ADYACENCY_MATRIX':
                #print "set ADJ [ ", s[1], " ] :=",
                adjlocs = list()
                for l in s[2:]:
                    adjlocs.append(l),
                ADJ[s[1]] = adjlocs
            if s[0] == 'LOCS':
                #print "set aLocs :="
                for l in s[1:]:
                    ALOCS.append(l)

            if s[0] == 'INITIAL_LOC':
                initLoc[s[1]] = s[2]
            if s[0] == 'MAX_TIME':
                maxTime = int(s[1])

            if s[0] == 'SEARCH_EFFICACY':
                expl[s[1],s[2],s[3]] = float(s[4])

            if s[0] == "RELATED_LOCS":
                rlocs = list()
                for l in s[2:]:
                    rlocs.append(l)
                riLoc[s[1]] = rlocs

            if s[0] == "RELATED_CELLS":
                rlocs = list()
                for l in s[2:]:
                    rlocs.append(l)
                rLoc[s[1]] = rlocs

            if s[0] == 'REACHABLE_DEMAND':
                reachable_demand = float(s[1])
            if s[0] == 'DEMAND':
                d[s[1]]=float(s[2])
            if s[0] == 'LOCATION_DISTANCE':
                li = int(s[1])
                lj = int(s[2])
                dist= float(s[3])
                d_matrix[li,lj] = dist
            if s[0] == 'LOC_COORDINATE':
                l = s[1]
                x = float(s[2])
                y = float(s[3])
                coos[l] = (x,y)
            if s[0] == 'COMPLETE_TIME_PER_TASK':
                if s[1] not in completeTimePerTask:
                    completeTimePerTask[s[1]]=dict()
                completeTimePerTask[s[1]][s[2]]=int(s[3])
            if s[0] == 'FIXED_ALLOCATION':
                a = s[1]
                fixed_alloc[a]=s[2:]

            if s[0] == 'FORBIDDEN_ALLOCATION':
                a = s[1]
                if a not in forbidden_alloc:
                    forbidden_alloc[a] = list()
                forbidden_alloc[a].append(s[2:])



#    print "# Agents ", len(A)
 #   print "# Cells ", len(CELLS)
    if len(coos)>0:
        USE_COO=True
#    print "USE_COO ",USE_COO
    if USE_COO:
        if not len(coos):
            print("No coordinates")
            exit(1)
        for (li,(xi,yi)) in coos.items():
            for (lj,(xj,yj)) in coos.items():
                dapprox = DAPPROX_C1*min( abs(xi-xj),abs(yi-yj)) +  DAPPROX_C2*max(abs(xi-xj),abs(yi-yj))
                d_matrix[li,lj] = dapprox

#    for a in A:
#        print "ALoc[%s] (%d)"%(a,len(ALoc[a]))
#    for c in CELLS:
#        print "riLoc ",c," ", riLoc[c]

#    print expl
    # add empty list for those without adjacent locs
    for l in ALOCS:
        if not ADJ.get(l):
            ADJ[l] = list()
    for c in CELLS:
        if not d.get(c):
            d[c] = 1.0
    if scale_factor == None:
        scale_factor = 1.0/reachable_demand
#        print "scale_factor ", scale_factor
#    print "MAXTIME ", maxTime

    EADJ = [(a,b) for a in ALOCS  for b in ADJ[a]]
#    print "EADJ ",len(EADJ)
    for a in A:
#        print initLoc[a]
        tmp1 = [('START',m) for m in [n for n in list(set(ADJ[initLoc[a]]) |
                                                      set([initLoc[a]]))]]
        #print "tmp1 ", tmp1
        tmp2 = [(m,'END') for m in ALoc[a]]
        #print "tmp2 ", tmp2, " ", len(tmp2)
        tmp3 = set(EADJ) | set(tmp1) | set(tmp2)
        tmp4 = set([(i,j) for i in (set(DUMMIES) | set(ALoc[a])) for j in
                    (set(DUMMIES) | set(ALoc[a]))])
        E[a] = tmp3 & tmp4
#        print "E[%s] (%d)"%(a,len(E[a]))
