#!/usr/bin/env python2.7

import subprocess
import time
from collections import defaultdict
from ansible.module_utils.basic import *

# What is the acceptable number of bytes on the interface for it to be "quiet"
BYTE_THRESHOLD = 10000 

# How many times should we check the interface
INTERFACE_CHECKS = 3

# How long between each interface check (in seconds)?
TIME_DELAY = 1


def get_interface_stats():
    '''
    get_interface_stats() - returns dict

    pulls the contents of /proc/net/dev
    and parses into dict of {interface: bytes}
    '''

    output = subprocess.check_output(["cat", "/proc/net/dev"])

    dev_lines = output.split("\n")

    interface_stats = dict()

    for line in dev_lines:
        temp_line = line.lstrip(" ")
        if temp_line.startswith("swp"):
            interface_stats[temp_line[:temp_line.find(":")]] = int(temp_line.split()[1])

    return interface_stats


def stat_difference(old_stats, new_stats):

    '''
    stat_difference(dict, dict) - returns dict

    take a historical interface stat snapshot dict (from get_interface_stats())
    and compare it to a new stats snapshot.

    Returns a dict of {interface: byte_difference}
    '''
    difference_dict = dict()

    for old_interface in old_stats.keys():
        if old_interface not in new_stats:
            # If the interface list changed, just move on.
            # there could be corner cases where this matters, 
            # but shouldn't for the proof of concept use case
            continue

        difference_dict[old_interface] = new_stats[old_interface] - old_stats[old_interface]

    return difference_dict


def is_traffic_drained(interface_stats_history):
    '''
    is_traffic_drained(tuple) - returns boolean

    consumes a tuple, which is the stats history that has been 
    collected for a single interface.
    Expected format is ("swp1", [1, 2, 3])

    is_traffic_drained will look at the stats and determine if the difference
    in byte counters is acceptable to determine that traffic is no longer flowing.

    This function is required becuase routing procols and broadcasts (or any link local traffic)
    will cause packet counters to continue to increment.

    returns True if the average byte difference is within BYTE_THRESHOLD
    returns False if the average byte difference is not within BYTE_THRESHOLD
    '''

    return (sum(interface_stats_history[1]) / len(interface_stats_history[1])) <= BYTE_THRESHOLD


def main():
    module = AnsibleModule(argument_spec=dict())
    interface_check_counter = 0
    old_stats = get_interface_stats()
    stats_history = defaultdict(list)
    time.sleep(TIME_DELAY)

    while interface_check_counter < INTERFACE_CHECKS:
        current_stats = get_interface_stats()

        for k, v in stat_difference(old_stats, current_stats).iteritems():
            stats_history[k].append(v)

        old_stats = current_stats
        time.sleep(TIME_DELAY)
        interface_check_counter += 1

    for interface, byte_list in stats_history.iteritems():
        if not is_traffic_drained((interface, byte_list)):
            # print "Traffic not drained from: " + interface
            # exit(1)
            module.fail_json(changed=False, msg="Traffic not drained from " + interface)

    module.exit_json(changed=False, msg="All traffic drained from device")

if __name__ == '__main__':
    main()
