# Resources for Ansible/Class Roster/AWS presentation

The deck for "Class Roster - Moving to Amazon Web Services with Ansible" (Eric Grysko; April 2016) is available as a [PDF](doc/SSIT-Ansible-ClassRoster-Apr2016.pdf).

This repository contains *examples* for illustration purposes of how Ansible is used for the Class Roster and other ways Ansible can be used.

Demo commands...

```
# Confirm our profile is set, using the CU Training account
export AWS_PROFILE=cu-training
export AWS_DEFAULT_PROFILE=cu-training

# create some security groups
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 demo_networking.yml

# Create some instances
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 --tags "provision" \
 demo_web_elb.yml

# basic config management
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 --tags "configure" \
 demo_web_elb.yml

# deploy some code
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 --tags "deploy" \
 demo_web_elb.yml

# Create an ELB and register our instances
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 --tags "elb" \
 demo_web_elb.yml
```


## Overview

**Directory Structure**
```
.
+-- doc/                              # documentation as necessary
+-- group_vars/                       # group specific variables
+-- host_vars/                        # host specific variables
+-- inventory/                        # static + dynamic inventory resources
|   +-- training/                     # pattern can support multiple accounts
+-- library/             
|   +-- ec2_elb_tag.py                # custom module to tag ELBs
+-- lookup_plugins/      
|   +-- ec2_vol_find_volume_id.py     # custom lookup plugin
+-- roles/               
|   +-- aws-network/                  # a reusable role defining our security groups
+-- templates/                        # globally available templates
|   +-- web-asg-userdata.j2           # template for EC2 userdata passed for ASG
+-- ansible.cfg                       # Ansible configuration
+-- aws-cu-training-vars.yml          # account variables for demo
+-- demo_*.yml                        # example playbooks
```
### Roles

* admin-users - Set admin & developer users on instance
* aws-network - Maintain security groups, RDS param groups, etc
* ec2-config - Extended by phpweb-config, common base settings
* phpweb-config - Our web instance
* phpweb-instance - For provisioning our EC2 instance. Set to **delete** volumes on instance termination.
* swapfile-config - Set swapfile

**Running a playbook**
```
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 playbook_name.yml
```

### Example: demo_ec2_state.yml

**Caution: You almost certainly do not want to run this playbook unless you specify a limit**

Uses --tags and --limit to target hosts. Failing to specify --limit will result in stopping ALL instances. All dynamic and static groups are available in limit.

```
# Based on an environment tag coming from dynamic
ansible-playbook -i inventory/training/ \
 -e "@aws-cu-training-vars.yml" \
 --tags "start-instance" \
 --limit tag_Environment_Demo \
 demo_ec2_state.yml

# Based on an environment tag coming from dynamic
ansible-playbook -i inventory/training/ \
  -e "@aws-cu-training-vars.yml" \
  --tags "stop-instance" \
  --limit tag_Environment_Demo \
  demo_ec2_state.yml
```

### Example: demo_web_elb.yml

Four main sections as identified by a tag

1. provision
2. configure
3. deploy
4. elb

### Example: demo_networking.yml

Update security groups.

### Example: demo_autoscaling.yml

Playbook creates an AMI to be used for an ASG. Create a new launch config and update ASG.

### Using vault

Your `ansible.cfg` should define where `vault_password_file` is located.
```
ansible-vault edit group_vars/tag_Name_demo_instance/file.yml
```

## References

* [ansible.com](https://www.ansible.com/)
* [Ansible - How Ansible Works](https://www.ansible.com/how-ansible-works)
* [Ansible - Cloud Modules](https://www.ansible.com/how-ansible-works)
* [Ansible - Best Practices](http://docs.ansible.com/ansible/playbooks_best_practices.html)
* [YAML: YAML Ain't Markup Language](http://yaml.org/) - yaml.org + spec
* [boto: A Python interface to Amazon Web Services](http://docs.pythonboto.org/en/latest/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
