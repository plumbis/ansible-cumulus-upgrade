from behave import *
import ansible.runner
import yaml
import json

'''
    Scenario: Check BGP Neighbors
    Given BGP is enabled
    when neighbors are configured
    then the neighbors should be up
'''

spine_vars_location = "../roles/spines/vars/main.yml"
leaf_vars_location = "../roles/leafs/vars/main.yml"
server_vars_location = "../roles/servers/vars/main.yml"

spine_interface_config = dict() 
leaf_interface_config = dict()
server_interface_config = dict()

spine_vars = dict()
leaf_vars = dict()
server_vars = dict()

list_of_leafs = []
list_of_spines = []
list_of_servers = []


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

    if "interfaces" in context.spine_vars.keys():
        for node in context.spine_vars["interfaces"]:
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

    if "interfaces" in context.leaf_vars.keys():
        for node in context.leaf_vars["interfaces"]:
            list_of_leafs.append(node)


def get_server_vars(context):
    '''
    Open the Ansible vars file for leafs and load it into server_vars
    '''
    global list_of_servers

    with open(server_vars_location) as stream:
        try:
            context.server_vars = yaml.load(stream)
        except yaml.YAMLError as exc:
            assert False, "Failed to load server variables file: " + exc

    if "interfaces" in context.server_vars.keys():
        for node in context.server_vars["interfaces"]:
            list_of_servers.append(node)


def get_spine_interfaces(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global spine_interface_config

    runner = ansible.runner.Runner(module_name='command', 
                                   module_args="netshow interface all -j",
                                   become=True, pattern=list_of_spines)

    ansible_output = runner.run()

    if ansible_output is None:
        assert False, "Ansible is unable to contact a spine"

    spine_interface_config = ansible_output["contacted"]


def get_leaf_interfaces(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global leaf_interface_config

    runner = ansible.runner.Runner(module_name='command', 
                                   module_args="netshow interface all -j",
                                   become=True, pattern=list_of_leafs)

    ansible_output = runner.run()

    if ansible_output is None:
        assert False, "Ansible is unable to contact a leaf"

    leaf_interface_config = ansible_output["contacted"]


def get_server_interfaces(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global server_interface_config

    runner = ansible.runner.Runner(module_name='command', 
                                   module_args="netshow interface all -j",
                                   become=True, pattern=list_of_servers)

    ansible_output = runner.run()

    if ansible_output is None:
        assert False, "Ansible is unable to contact a server"

    server_interface_config = ansible_output["contacted"]


@given('an interface is configured')
def step_impl(context):

    # Setup: Load Vars
    get_spine_vars(context)
    get_leaf_vars(context)
    get_server_vars(context)

    # Setup: Load Config
    get_spine_interfaces(context)
    get_leaf_interfaces(context)
    get_server_interfaces(context)

    # Only checking that BGP is in the vars file (i.e., it should be enabled)
    if not len(list_of_spines) > 0:
        assert False, "No interfaces defined in ANsible vars file for spines" 
    if not len(list_of_leafs) > 0:
        assert False, "No interfaces defined in Ansible vars files for leafs"
    if not len(list_of_servers) > 0:
        assert False, "No interfaces defined in Ansible vars files for servers"

    assert True


@then('the interfaces should be up')
def step_impl(context):

    for spine in list_of_spines:
        json_data = json.loads(spine_interface_config[spine]["stdout"])
        var_interface_list = context.spine_vars["interfaces"][spine].keys()

        for interface in var_interface_list:
            if json_data[interface]["linkstate"] == "UP":
                continue
            else:
                assert False, "Interface " + interface + " on " + spine + " is in state " + json_data[interface]["linkstate"]

    for leaf in list_of_leafs:
        json_data = json.loads(leaf_interface_config[leaf]["stdout"])
        var_interface_list = context.leaf_vars["interfaces"][leaf].keys()

        for interface in var_interface_list:
            if json_data[interface]["linkstate"] == "UP":
                continue
            else:
                assert False, "Interface " + interface + " on " + leaf + " is in state " + json_data[interface]["linkstate"]

    for server in list_of_servers:
        json_data = json.loads(server_interface_config[server]["stdout"])
        var_interface_list = context.server_vars["interfaces"][server].keys()

        for interface in var_interface_list:
            if json_data[interface]["linkstate"] == "UP":
                continue
            else:
                assert False, "Interface " + interface + " on " + server + " is in state " + json_data[interface]["linkstate"]

    assert True
