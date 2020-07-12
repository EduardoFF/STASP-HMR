docker run -it  --rm \
       --env="DISPLAY" \
       --env="QT_X11_NO_MITSHM=1" \
       --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
       -v /home/eduardo/swarmix_experiments:/swarmix_experiments \
       --privileged \
       --net="host"\
       eduardo:swarmix-full \
       /launch/simulator ${@:1}

#amd64/ubuntu:xenial \
#       -v /opt/ibm/ILOG/CPLEX_Studio126:/cplex \
