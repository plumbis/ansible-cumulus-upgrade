# Interop 2016 - Network Continuous Integration

## Introduction
This is a fully automated network with servers running Apache connected. 100% of the configuration is managed through git and Ansible. 

The goal of this project is to demonstrate how CI tools like [GitLab-CI](https://about.gitlab.com/gitlab-ci/) can be leveraged to automatically spin up a virtual networking environment and automatically run integration tests against the network for any proposed changes. 

## Diagrams:
![Diagram](diagram.png)

## Routing
Server to leaf and leaf to spine routing utilize eBGP. 

The [BGP unnumbered](https://docs.cumulusnetworks.com/display/DOCS/Configuring+Border+Gateway+Protocol+-+BGP#ConfiguringBorderGatewayProtocol-BGP-unnumberedUsingBGPUnnumberedInterfaces) feature is used so that no IP addresses are required for any infrastructure links.

All devices have unique /32 IPv4 and /128 IPv6 loopback addresses configured.

Each device announces only their loopback IPv4 and IPv6 addresses into the network. No other routes are advertised via BGP.

## Server Configuration
For networking simplicity the webservers are represented by Cumulus Vx nodes. Ubuntu could be used with slight modifications to the Behave checks and some additional work with the Ansible playbooks.

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
### GitLab
[GitLab](https://gitlab.com/) is a git repository, similar to [GitHub](http://www.github.com). GitLab provides built file management and change tracking and collaboration, just like GitHub. The reason GitLab is used over GitHub was for the ability to integrate issue tracking, the build process and file storage all under one roof. The concepts demonstrated here could easily be broken out to using GitHub with [Jenkins](http://jenkins-ci.org) or [Stash](https://www.atlassian.com/software/bitbucket/server) with [Bamboo](https://www.atlassian.com/software/bamboo)

# Files
* `.gitlab-ci.yml` - This file is used by GitLab to define when to build the project and what to execute when a new commit is made through git. Syntax for the gitlab-ci file can be found on the [GitLab site](http://doc.gitlab.com/ce/ci/).
* `README.me` - The README.me file is where this content you are reading is generated from. It is the documentation for the parent project
* `Vagrantfile` - Vagrant reads the Vagrantfile to determine how to build the virtual environment, virtually connect the devices together and how to execute the automation engine (Ansible in this case). 
* `ansible.cfg` - Local settings for Ansible. Prevents conflicts with global Ansible settings.
* `diagram.png` - Topology diagram of the lab
* `lab.yml` - The main playbook to configure the lab. Running this playbook will trigger provisioning of the entire lab.
* `linter.sh` - This is a bash script that will validate all `.yml` files in the project for valid Yaml syntax.

# Requirements
The following are a list of required software to run this project.
* **[Vagrant](https://www.vagrantup.com/)**
* **[VirtualBox](https://www.virtualbox.org/wiki/Downloads)**
* **[Ansible](http://ansible.com)**

In order to run the test cases manually, the following tools are required
* **[Yamllint](https://pypi.python.org/pypi/yamllint)** - an open source python script that will validate YAML files for proper syntax. `pip install yamllint` 
* **[Behave](https://pythonhosted.org/behave/install.html)** - Due to an issue with displaying color in Behave, you will have to manually modify two Behave files after install to have it support color in GitLab. Make the changes described in this [diff](https://github.com/behave/behave/commit/5fa2dd3fd1dc7149857df4da156d8fd00f5058a5). 
If you do not want to modify the files, edit `.gitlab-ci.yml` and remove `--force-color` from the line `behave --force-color`.


In order to build this project automatically, the following tools are also required
* **[Git](https://git-scm.com/)**
* **[GitLab Runner](https://gitlab.com/gitlab-org/gitlab-ci-multi-runner#installation)** - a program that runs locally to execute the build process.

# The Build Process
Continous Integration/Continous Development (CI/CD) Pipelines like GitLab, Jenkins, Travis-CI or many others can hook directly into Git commits. When new code is pushed to the central Git repository the build tool can then execute predefined steps to "build" the software.

In this case it is not software that is being written, but configurations for servers and network. Instead of compiling a C program, we will build a virtual environment that represents the production systems and execute pre-defined tests against this virtual environment. 

More specifically, when a `git commit` is executed, GitLab will contact a pre-defined [gitlab runner](https://gitlab.com/gitlab-org/gitlab-ci-multi-runner). A GitLab runner is an agent running on a server (or your laptop) with the required tools installed.

When GitLab automatically contacts the GitLab runner, it will run the steps defined in `.gitlab-ci.yml`. Specifically the following actions will be taken:
1.) It will enter the directory `/Users/plumbis/vagrant/interop-2016/validation` and issue `vagrant destroy -f` in order to clean up any previously running lab
2.) The script `linter.sh` will run. It will find all .yaml files and check them for valid syntax
3.) The is launched with the `vagrant up` command (--color is required to print color in the build tool). As defined in the `Vagrantfile` the Ansible automation configuration is also applied at this time. 
4.) A 10 second delay is implemented to allow the system to converge
5.) The Behave validation scripts are executed (the --force-color argument is required to show color in the build tool)
6.) The lab is then destroyed with `vagrant destroy -f`

The actions that can be done within the build process are entirely flexible and can be as simple as running commands directly on the `GitLab Runner` node or more complex CI/CD toolchains (which are beyond the scope of this project).
