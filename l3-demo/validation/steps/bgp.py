from behave import *
import ansible.runner
import yaml
import json
import subprocess
import time
import shutil
import os

'''
    Scenario: Check BGP Neighbors
    Given BGP is enabled
    when neighbors are configured
    then the neighbors should be up
'''

spine_vars_location = "../roles/spines/vars/main.yml"
leaf_vars_location = "../roles/leafs/vars/main.yml"
server_vars_location = "../roles/servers/vars/main.yml"

spine_bgp_neighbor_config = dict() 
leaf_bgp_neighbor_config = dict()
server_bgp_neighbor_config = dict()

#spine_vars = dict()

list_of_leafs = []
list_of_spines = []
list_of_servers = []

def run_ansible_command(context, ansible_group_list, command):
    '''
    Takes in a list of ansible nodes and a command 
    and executes an ansible ad hoc command.

    In Ansible 2.0 the Ansible API no longer uses ansible.runner()
    Ansible has also stated that the Ansible API may change at any time.
    To prevent bad things from happening this is implemented with 
    ad hoc commands on the local machine.

    Also, Ansible can only return structured data for ad hoc commands with the 
    --tree argument which only writes to a file.

    Consumes list and string.
    Returns dict of json output
    ''' 

    timestamp = time.time()

    directory_name = ".behave_ansible_" + str(timestamp)
    node_string = ":".join(ansible_group_list)
    command = ["ansible", node_string, "-a", command, "--become", "--tree", directory_name]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    if stderr:
        assert False, "\nCommand: " + " ".join(command) + "\n" + "Ansible Error: " + stderr
    else:

        node_output = dict()

        for file in os.listdir(directory_name):

            with open(directory_name + "/" + file) as data_file:
                data = json.load(data_file)

            node_output[file] = data

        shutil.rmtree(directory_name)
        return node_output

    shutil.rmtree(directory_name)
    assert False, "Error in run_ansible_command. Not sure how we got here."


def get_spine_vars(context):
    '''
    Open the Ansible vars file for spines and load it into spine_vars
    '''
    global list_of_spines

    with open(spine_vars_location) as stream:
        try:
            context.spine_vars = yaml.load(stream)
        except yaml.YAMLError as exc:
            assert False, "Failed to load spine variables file: " + exc

    if "bgp" in context.spine_vars.keys():
        for node in context.spine_vars["bgp"]:
            list_of_spines.append(node)


def get_leaf_vars(context):
    '''
    Open the Ansible vars file for leafs and load it into leaf_vars
    '''
    global list_of_leafs

    with open(leaf_vars_location) as stream:
        try:
            context.leaf_vars = yaml.load(stream)
        except yaml.YAMLError as exc:
            assert False, "Failed to load leaf variables file: " + exc

    if "bgp" in context.leaf_vars.keys():
        for node in context.leaf_vars["bgp"]:
            list_of_leafs.append(node)


def get_server_vars(context):
    '''
    Open the Ansible vars file for leafs and load it into servers_vars
    '''
    global list_of_servers

    with open(server_vars_location) as stream:
        try:
            context.server_vars = yaml.load(stream)
        except yaml.YAMLError as exc:
            assert False, "Failed to load server variables file: " + exc

    if "bgp" in context.server_vars.keys():
        for node in context.server_vars["bgp"]:
            list_of_servers.append(node)


def get_spine_bgp_neighbors(context):
    ''' 
    Pull the BGP neighbor configuration directly from the devices
    '''
    global spine_bgp_neighbor_config

    spine_bgp_neighbor_config = run_ansible_command(context, list_of_spines, "cl-bgp summary show json")

def get_leaf_bgp_neighbors(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global leaf_bgp_neighbor_config

    leaf_bgp_neighbor_config = run_ansible_command(context, list_of_leafs, "cl-bgp summary show json")

def get_server_bgp_neighbors(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global server_bgp_neighbor_config

    server_bgp_neighbor_config = run_ansible_command(context, list_of_servers, "cl-bgp summary show json")


def get_spine_config_ports(context):
    '''
    Extract the interface list from the configured node. 
    '''
    global spine_bgp_neighbor_config

    return_dict = dict()

    for spine in list_of_spines:
        if spine_bgp_neighbor_config[spine]["stdout"] == "":
            assert False, "No BGP configuration found on " + spine

        else:
            json_data = json.loads(spine_bgp_neighbor_config[spine]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + spine

            return_dict[spine] = json_data["peers"].keys()


def get_leaf_config_ports(context):
    '''
    Extract the interface list from the configured node.
    '''

    global leaf_bgp_neighbor_config

    for leaf in list_of_leafs:
        if leaf_bgp_neighbor_config[leaf]["stdout"] == "":
            assert False, "No BGP configuration found on " + leaf

        else:
            json_data = json.loads(leaf_bgp_neighbor_config[leaf]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + leaf

            return json_data["peers"].keys()


def get_server_config_ports(context):
    '''
    Extract the interface list from the configured node.
    '''

    global servers_bgp_neighbor_config

    for server in list_of_servers:
        if server_bgp_neighbor_config[server]["stdout"] == "":
            assert False, "No BGP configuration found on " + server

        else:
            json_data = json.loads(server_bgp_neighbor_config[server]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + server

            return json_data["peers"].keys()


@given('BGP is enabled')
def step_impl(context):

    # Setup: Load Vars
    get_spine_vars(context)
    get_leaf_vars(context)
    get_server_vars(context)

    # Setup: Load Config
    get_spine_bgp_neighbors(context)
    get_leaf_bgp_neighbors(context)
    get_server_bgp_neighbors(context)

    # Only checking that BGP is in the vars file (i.e., it should be enabled)
    if not len(list_of_spines) > 0:
        assert False, "No BGP peers defined in Ansible vars file for spines"
    if not len(list_of_leafs) > 0:
        assert False, "No BGP peers defined in Ansible vars file for leafs"
    if not len(list_of_servers) > 0:
        assert False, "No BGP peers defined in Ansible vars file for servers"
    else:
        assert True


@when('neighbors are configured')
def step_impl(context):
    '''
    Actually check that the BGP config was pushed to the box 
    and that the number of peers on the box matches what we expect
    '''

    spine_var_ports = dict()
    spine_config_ports = dict()

    leaf_var_ports = dict()
    leaf_config_ports = dict()

    server_var_ports = dict()
    server_config_ports = dict()

    # Iterate over Spine Variables File
    if "bgp" in context.spine_vars:
            for spine in context.spine_vars["bgp"].keys():
                if "fabric_ports" in context.spine_vars["bgp"][spine]:
                    spine_var_ports[spine] = context.spine_vars["bgp"][spine]["fabric_ports"]
                else:
                    assert False, "fabric_ports not defined in Ansible vars file for " + spine

    # Iterate over Leaf Variables File
    if "bgp" in context.leaf_vars:
        for leaf in context.leaf_vars["bgp"].keys():
            leaf_var_ports[leaf] = []
            if "fabric_ports" in context.leaf_vars["bgp"][leaf]:
                leaf_var_ports[leaf].extend(context.leaf_vars["bgp"][leaf]["fabric_ports"])
            else:
                assert False, "fabric_ports not defined in Ansible vars file for " + leaf

            if "server_ports" in context.leaf_vars["bgp"][leaf]:
                leaf_var_ports[leaf].extend(context.leaf_vars["bgp"][leaf]["server_ports"])
            else:
                assert False, "server_ports not defined in Ansible vars file for " + leaf

    # Iterate over Server Variables File
    if "bgp" in context.server_vars:
        for server in context.server_vars["bgp"].keys():
            if "tor_ports" in context.server_vars["bgp"][server]:
                server_var_ports[server] = context.server_vars["bgp"][server]["tor_ports"]
            else:
                assert False, "tor_ports not defined in Ansible vars file for " + server

    for spine in list_of_spines:
        if spine_bgp_neighbor_config[spine]["stdout"] == "":
            assert False, "No BGP configuration found on " + spine
        else:
            json_data = json.loads(spine_bgp_neighbor_config[spine]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + spine

            # convert unicode elements to ascii
            spine_config_ports[spine] = [s.encode('ascii') for s in json_data["peers"].keys()]

    for leaf in list_of_leafs:
        if leaf_bgp_neighbor_config[leaf]["stdout"] == "":
            assert False, "no BGP configuration found on " + leaf
        else:
            json_data = json.loads(leaf_bgp_neighbor_config[leaf]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + leaf

            # convert unicode elements to ascii
            leaf_config_ports[leaf] = [s.encode('ascii') for s in json_data["peers"].keys()] 

    for server in list_of_servers:
        if server_bgp_neighbor_config[server]["stdout"] == "":
            assert False, "no BGP configuration found on " + server
        else:
            json_data = json.loads(server_bgp_neighbor_config[server]["stdout"])

            if len(json_data["peers"]) == 0:
                assert False, "No peers found on " + server

            # convert unicode elements to ascii
            server_config_ports[server] = [s.encode('ascii') for s in json_data["peers"].keys()] 

    for spine in spine_var_ports:
        if not set(spine_var_ports[spine]) == set(spine_config_ports[spine]):
            assert False, "Configured spine ports do not match variables file ports for " + spine

    for leaf in leaf_var_ports:
        if not set(leaf_var_ports[leaf]) == set(leaf_config_ports[leaf]):
            assert False, "Configured leaf ports do not match variables file ports for " + leaf

    for server in server_var_ports:
        if not set(server_var_ports[server]) == set(server_config_ports[server]):
            assert False, "Configured server ports do not match variables file ports for " + server

    assert True


@then('the neighbors should be up')
def step_impl(context):
    '''
    Validate that the BGP state from Ansible is "Established"
    '''

    global spine_bgp_neighbor_config, list_of_spines
    global leaf_bgp_neighbor_config, list_of_leafs
    global server_bgp_neighbor_config, list_of_server

    for spine in list_of_spines:
        json_data = json.loads(spine_bgp_neighbor_config[spine]["stdout"])

        neighbor_list = json_data["peers"].keys()

        for neighbor in neighbor_list:
            if not json_data["peers"][neighbor]["state"] == "Established":
                assert False, spine + " peer " + neighbor + " not Established. Current state: " + json_data["peers"][neighbor]["state"]

    for leaf in list_of_leafs:
        json_data = json.loads(leaf_bgp_neighbor_config[leaf]["stdout"])

        neighbor_list = json_data["peers"].keys()

        for neighbor in neighbor_list:
            if not json_data["peers"][neighbor]["state"] == "Established":
                assert False, leaf + " peer " + neighbor + " not Established. Current state: " + json_data["peers"][neighbor]["state"]

    for server in list_of_servers:
        json_data = json.loads(server_bgp_neighbor_config[server]["stdout"])

        neighbor_list = json_data["peers"].keys()

        for neighbor in neighbor_list:
            if not json_data["peers"][neighbor]["state"] == "Established":
                assert False, server + " peer " + neighbor + " not Established. Current state: " + json_data["peers"][neighbor]["state"]

    assert True
