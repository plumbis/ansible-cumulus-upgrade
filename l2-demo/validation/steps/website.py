from behave import *
import ansible.runner
import yaml
import json

'''
    Scenario: Validate Web Server Access
    Given a webserver is configured
    Then the website should be accessable
'''

server_vars_location = "../roles/servers/vars/main.yml"

server_v4_dict = dict()
server_v6_dict = dict()
server_loopback_config = dict()
list_of_servers = []


def get_server_vars(context):
    '''
    Open the Ansible vars file for leafs and load it into
    server_v4_dict and server_v6_dict
    '''

    with open(server_vars_location) as stream:
        try:
            context.server_vars = yaml.load(stream)
        except yaml.YAMLError as exc:
            assert False, "Failed to load server variables file: " + exc

    if "interfaces" in context.server_vars.keys():
        for node in context.server_vars["interfaces"]:
            found_loopback = False
            interfaces = context.server_vars["interfaces"][node]

            if "lo" in interfaces.keys():
                if "ipv4" in interfaces["lo"].keys():
                    server_v4_dict[node] = interfaces["lo"]["ipv4"]
                    found_loopback = True

                if "ipv6" in interfaces["lo"].keys():
                    server_v6_dict[node] = interfaces["lo"]["ipv6"]
                    found_loopback = True

            if found_loopback:
                list_of_servers.append(node)


def get_configured_loopbacks(context):
    ''' 
    Make Ansible API call to pull data directly from the node.
    Return data in json format
    '''
    global server_loopback_config

    runner = ansible.runner.Runner(module_name='command', 
                                   module_args="netshow interface lo -j",
                                   become=True, pattern=list_of_servers)

    ansible_output = runner.run()

    if ansible_output is None:
        assert False, "Ansible is unable to contact a leaf"

    server_loopback_config = ansible_output["contacted"]


def check_apache_service(context):
    ''' 
    Make Ansible API call to validate apache2 is running
    '''

    runner = ansible.runner.Runner(module_name='service', 
                                   module_args="name=apache2 state=started enabled=yes",
                                   check=True, become=True, pattern=list_of_servers)

    ansible_output = runner.run()

    if ansible_output is None:
        assert False, "Ansible is unable to contact a leaf"

    for node in ansible_output["contacted"].keys():
        if "msg" in ansible_output["contacted"][node]:
            if "service state changed" in ansible_output["contacted"][node]["msg"]:
                assert False, "Apache configure but not running on " + node
            if "no service" in ansible_output["contacted"][node]["msg"]:
                assert False, "Apache not configured on " + node

        elif ansible_output["contacted"][node]["state"] == "started":
            assert True

        else:
            assert False, "Unknown Apache status check error output dump:" + node


def check_webserver(context):

    for node in context.loopback_dict.keys():
            list_of_loopbacks = context.loopback_dict.values()

            for ip in list_of_loopbacks:
                runner = ansible.runner.Runner(module_name='uri', 
                                               module_args="url=http://" + ip[:ip.find("/")],
                                               pattern=node)

                ansible_output = runner.run()

                if ansible_output is None:
                    assert False, "Ansible is unable to contact a leaf"

                if "msg" in ansible_output["contacted"][node]:
                    assert False, "Ansible Error: " + ansible_output["contacted"][node]["msg"]

                if "status" not in ansible_output["contacted"][node]:
                    assert False, "Unknown Ansible error trying to contact http://" + \
                                  ip[:ip.find("/")] + " from " + node + ". Ansible output: " + \
                                  ansible_output["contacted"][node]

                if not ansible_output["contacted"][node]["status"] == 200:
                    assert False, "Server on " + node + " did not return 200 OK code. Returned " + str(ansible_output["contacted"][node]["status"])


@given('a webserver is configured')
def step_impl(context):

    # Setup: Load Vars File
    get_server_vars(context)

    # Setup: Pull Loopback Interface Config from Device
    get_configured_loopbacks(context)

    assert True


@when('apache is running')
def step_impl(context):

    check_apache_service(context)

    assert True


@then('the website should be accessable')
def step_impl(context):
    '''
    Validate that the servers can reach each other's webservers
    '''

    if len(server_v4_dict) > 0:
        context.loopback_dict = server_v4_dict

        check_webserver(context)

    # TODO: Ansible URI module doesn't seem to like IPv6
    # if len(server_v6_dict) > 0:
    #     context.loopback_dict = server_v6_dict

        check_webserver(context)

    assert True
