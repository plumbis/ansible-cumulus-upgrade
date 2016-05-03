## Automated Topology Deployments Using Ansible

#### Notes on the Automation:
Vagrant creates a NAT network with eth0 of all Cumulus VX and Ubuntu boxes, forwarding a localhost TCP port to port 22 of the guest for SSH access. This is how the wrapper ```vagrant ssh <vm>``` works.

While this works well for purely local SSH access, it inherently makes it hard to connect and develop with these devices as if they were actual remote network nodes. If you do want the ```ssh vagrant@vm``` style access expected of real hosts, consider using the Vagrant-to-Local script available at the following link. This is **not** required for this demo.

* https://github.com/slaffer-au/vagrant-to-local

##### Setting Up for Automation
1. Change to the automation directory
2. Ensure all hosts are accessible by Ansible with the ad-hoc command ```ansible all -m ping -u vagrant```.


---


#### Two-Tier CLAG:
![Topology](https://github.com/slaffer-au/vx_vagrant_one_stop_demo/blob/master/Topology/two-tier-clag-topology.png)

##### Description:
A common deployment seen in data centers involves Multi-Chassis Link Aggregation, or MLAG, where two switches with independant control-planes emulate a single logical device to directly connected devices, allowing a more complete use of bandwidth and available redundancy.

This topology demonstrates a deployment of Cumulus Link Aggregation (CLAG) and Cumulus Virtual Router Redundancy (VRR).
  * http://docs.cumulusnetworks.com/display/DOCS/Multi-Chassis+Link+Aggregation+-+MLAG
  * http://docs.cumulusnetworks.com/display/DOCS/Virtual+Router+Redundancy+-+VRR

##### Details:
  * CLAGs are formed as pictured above, with CLAG IP keepalive and messaging communication performed using interface _peerlink.4094_.
  * No CLAG backup IP is configured. In a real-world deployment, it is recommended to do this through the OOB network.
  * On the Spine switches, CLAG IDs 1-3 are used towards the Leaf switches. Each Leaf pair use only CLAG ID 1 towards the Spines.
  * A CLAG ID 5 is configured to the hosts. The hosts's bond interface is named "bond0".
  * Each switch uses a VLAN-aware bridge, trunking VLANs 1-100 with a native VLAN of 1.
  * SVIs are configured on VLAN 10 on all switches. The Spine switches also have VRR configured between them in VLAN 10 to provide gateway redundancy for the hosts.
  * The hosts are configured with a VLAN 10 address and an address in the native VLAN (not pictured).
  
##### Deployment:
1. Ensure "spine3" is commented out in the ```hosts``` file.
2. Run the Ansible playbook with the command ```ansible-playbook two-tier-clag.yml```.

---  



##### Details:
  * All hosts are assigned a loopback address. The same address is also assigned to the unnumbered interfaces between Leaf and Spine.
  * BGP is configured on all unnumbered interfaces, rather than with an IPv4 neighbor statement.
  * The BGP peer-group is configured with extended next-hop encoding and ```remote-as external``` or ```remote-as internal``` based on the demo.
  * All hosts advertise their loopbacks into BGP. All Leaf switches advertise their locally connected VLAN 10 subnet as pictured. SVIs and VRR is configured on VLAN 10 on all Leaf switches.
  * The Leaf to Host CLAG topology is retained, with CLAG ID 5 being configured to the hosts. Each Leaf switch maintains a VLAN-aware bridge, trunking VLANs 1-100 with a native VLAN of 1.
  * The hosts are configured with a VLAN 10 address unique to their attached Leaf pair as pictured.
  * Hosts host12 and host34 also have an address of `70.70.1.1` to emulate an anycast application. This host route is also advertised into BGP by leaf1-4 by a filtered redistribution of static routes. 
  * Host host56 maintains a static route to this anycast prefix with a next-hop of its local VRR address. 
  * For security, hosts do not have routes to the "infrastructure" subnets by design. While traffic will reach the hosts from the unnumbered infrastucture, hosts will only respond to addresses in the ```10.0.0.0/8``` range.
  
##### Deployment:
1. Run the Ansible playbook with the command ```ansible-playbook ebgp-unnum.yml``` or ```ansible-playbook ibgp-unnum.yml```.
2. If a nine switch topology is desired, uncomment "spine3" from the hosts file and run the Ansible playbook again to provision spine3.

---  

