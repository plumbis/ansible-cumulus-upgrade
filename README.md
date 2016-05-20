# Cumulus Linux Rolling Upgrade Demo

## Introduction
This demo will show how to use Ansible, Behave and Cumulus Linux to execute fully automated rolling upgrades of both a layer 3 and layer 2 (mLAG) network. 

To start the demo, navigate to either the layer 2 or layer 3 folder and "vagrant up". Caution: Attempting to "vagrant up" from the main project folder will result in an initialization error. 

## Tools
### Ansible
All configuration is driven through [Ansible](http://ansible.com). The intention is for no change to be made directly on the network and all changes to be done through modifications to the playbooks and/or variables (var) files.
### Behave
[Behave](https://pythonhosted.org/behave/) is a tool that allows for tests cases that can be written in human readable, English language, formats. These tests are then translated behind the scenes into python code to be executed to determine if the test passed or failed. All behave tests are located in the `/validation` directory. An example of a Behave test would be
```
Feature: Validate BGP

    Scenario: Check BGP Neighbors
    Given BGP is enabled
    when neighbors are configured
    then the neighbors should be up
```
To build a Behave test the natural langauge test is written in `/validation/test_name.feature`. Behave will automatically look for `/validation/steps/test_name.py` to execute the tests. For more information please reference the [Behave website](https://pythonhosted.org/behave/).
### VirtualBox
[VirtualBox](https://www.virtualbox.org/wiki/Downloads) is the Hypervisor that is used to run the Cumulus Linux virtual machines.
### Vagrant
[Vagrant](https://www.vagrantup.com/) is used to orchestrate VirtualBox and spin up the entire lab of nodes with all associated connectivity. 
### Cumulus Linux
[Cumulus Linux - CumulusVx](http://cumulusnetworks.com/cumulus-vx/) is used as the networking layer. CumulusVx is the virtual machine for testing Cumulus Linux production configuration. 
### Git
[Git](https://git-scm.com/) is used for all configuration file management. This allows for changes on a file and project level. 

# Files
* `README.me` - The README.me file is where this content you are reading is generated from. It is the documentation for the parent project
* `linter.sh` - This is a bash script that will validate all `.yml` files in the project for valid Yaml syntax.

# Requirements
The following are a list of required software to run this project.
* **[Vagrant](https://www.vagrantup.com/)**
* **[VirtualBox](https://www.virtualbox.org/wiki/Downloads)**
* **[Ansible](http://ansible.com)** - This has been tested on both Ansible 1.9 and Ansible 2.0. Behave validation is only supported on Ansible 1.9 due to Ansible 2.0 issue with `--tree`
* **[Yamllint](https://pypi.python.org/pypi/yamllint)** - an open source python script that will validate YAML files for proper syntax. `pip install yamllint` 
* **[Behave](https://pythonhosted.org/behave/install.html)**

# Helpful Links
The following are helpful links with instruction to getting the environment up and running.
* ** [Cumulus VX] (https://docs.cumulusnetworks.com/display/VX/Using+Cumulus+VX+with+Vagrant)** - This pages runs through how to setup the Vagrant environment for Cumulus VX, as well as how to do some basic navigation around Vagrant.
* ** [Ansible Install](http://docs.ansible.com/ansible/intro_installation.html)** - Ansible Installation guide.
* ** [Cumulus Ansible Modules] (https://support.cumulusnetworks.com/hc/en-us/articles/204255593-Ansible-Utilizing-Cumulus-Linux-Ansible-Modules)** Quick tutorial on how to use Cumulus Ansible Modules.
