import sys
from optparse import OptionParser
import model_data as Data



if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    if len(args) != 1:
        print("Invalid number of arguments")
        sys.exit()
    Data.readMDATA(args[0])
    print("Parsed instance: ")
    print("       number of tasks: ", len(Data.CELLS))
    print("       number of agents: ",len(Data.A))  # agent 0 is a dummy agent (central controller, if it exists)
    print("       max timespan: ",Data.maxTime) #time horizon for a plan
