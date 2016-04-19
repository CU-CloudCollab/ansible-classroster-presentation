# README - group_vars/


## SSIT Notes

* emg33: RDS instances come down thru dynamic inventory without hyphen to underscore conversion!

## Useful Ansible Doc Reference

#### group_vars/ location

http://docs.ansible.com/ansible/intro_inventory.html#groups-of-groups-and-group-variables

Tip: In Ansible 1.2 or later the group_vars/ and host_vars/ directories can exist in either the playbook directory OR the inventory directory. If both paths exist, variables in the playbook directory will override variables set in the inventory directory.

#### Variable precendence

In 2.x we have made the order of precedence more specific (last listed wins):

* role defaults [1]
* inventory vars [2]
* inventory group_vars
* inventory host_vars
* playbook group_vars
* playbook host_vars
* host facts
* registered vars
* set_facts
* play vars
* play vars_prompt
* play vars_files
* role and include vars
* block vars (only for tasks in block)
* task vars (only for the task)
* extra vars
