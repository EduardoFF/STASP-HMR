#!/bin/bash
# Usage:  bash run_simulator.sh <output folder> instance-id agents
# example: bash run_simulator.sh /home/eduardo/stasp/tests L10-R1-1 n4t2-1

SHAREDVOL=$1
docker run -it  --rm \
       --env="DISPLAY" \
       --env="QT_X11_NO_MITSHM=1" \
       --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
       -v ${SHAREDVOL} \
       --privileged \
       --net="host"\
       eduardofeo/swarmix:full \
       /launch/simulator ${@:2} -ep ${SHAREDVOL}
