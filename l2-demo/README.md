# Cumulus Linux Rolling Upgrade Demo - Layer 2 Example

## Introduction
This demo will show how to use Ansible, Behave and Cumulus Linux to execute fully automated rolling upgrades of a layer 2 MLAG network. Traffic will be drained and validated before a switch is upgraded. After the upgrade traffic will be brought back online, validated and the second device will be upgraded. 

The Vagrantfile used to build the demo network utilizes the latest Cumulus VX image available. If there is a specific VX image you'd like to use, please edit this parameter in the Vagrantfile.

## Network Diagram:
The topology for this demo can be seen here.
![Diagram](L2 topology.png)
[//]: # " Diagram located at: https://docs.google.com/drawings/d/1f7YIGF2dTdaFvvdVucxaEv-kGkqJrdd_Z-Xt38xARDk/edit"

## Connectivity
Each host is using [Multi-Chassis Link Aggregation (MLAG)](https://docs.cumulusnetworks.com/display/DOCS/Multi-Chassis+Link+Aggregation+-+MLAG) to both leaf switches. All leaf switches are using MLAG to the spine layer. 

Each device is using LACP and STP. MLAG peers will be using peerlinks and backup links as to avoid split brain issues. To drain the B side for the initial upgrade, the peerlinks will be disabled to switch traffic over to the A side exclusively.

## The Upgrade Process
Each server is connected to two leafs. The leftmost leaf will be considered to be in an "A" group. The rightmost leaf will be considered to be in a "B" group. The upgrade process will be on a datacenter wide basis, meaning all "A" switches will be run in parallel, and the same for all "B" switches.

For the spine devices, the same principals will be used, but on a single spine at a time.

### Staging the Upgrade
Before the upgrade is executed, all A devices will use BGP AS Path prepending to force all traffic both from the spines as well as the servers to prefer the B switch. 

Utilizing [Behave](https://pythonhosted.org/behave/) testing, each A device will be checked that no traffic is flowing before any intrusive changes are made.

### Executing the Change
In this virtual environment the upgrade will be simulated via the `reboot` command. In a production environment a software upgrade would execute in an identical manner.

### Post-Change Validation
When the device comes back online traffic will still route around it, as a result of the previously applied AS Path Prepend. 

Before any additional changes are made, Behave will once again execute tests to verify that the network is in a stable state. 

### Restoring Traffic
After the stability tests have passed the AS Path Prepend will be removed, allowing traffic to utilize both the "A" and "B" switch. 

At this point a final validation will run to verify that traffic is flowing as expected. 

Once the final validation passes the process will repeat for the "B" side switches.
