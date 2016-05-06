# not yet functional, having a hard time getting this to work against the vagrant environment
#! /bin/bash
#!/bin/bash
HOSTS="leaf1 leaf2 leaf3 leaf4 leaf5 leaf6 spine1 spine2"
SCRIPT="hostname; sudo clagctl; sudo brctl show; sudo brctl showmacs br0; sudo brctl showstp br0; sudo ifquery -a; sudo ip link show; exit"
for HOSTNAME in ${HOSTS} ; do
    vagrant ssh ${HOSTNAME} "${SCRIPT}"
done
