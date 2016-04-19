#!/usr/bin/python
#
# (c) 2015, Eric Grysko <eric@ericgrysko.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_elb_tag
short_description: Create and remove tag(s) from an EC2 ELB.
description:
    - Creates, removes and lists tags for an EC2 ELB.
requirements: [ boto, botocore, boto3 ]
author: "Eric Grysko(@ericgrysko)"
version_added: "2.1"
options:
  name:
    description:
      - The name of the ELB
    required: true
    default: None
  state:
    description:
      - Whether the tags should be present or absent on the ELB. Use list to interrogate the tags of an ELB.
    required: false
    default: present
    choices: ['present', 'absent', 'list']
  tags:
    description:
      - a hash/dictionary of tags to add to the ELB; '{"key":"value"}' and '{"key":"value","key":"value"}'
    required: true
    default: null

extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Simple example of confirming a tag
- name: Ensure tag present on balancer
  ec2_elb_tag:
    name: lb-classroster
    state: present
    tags:
      Environment: Test
      Product: ClassRoster
  register: task_output

# Remove a tag
- name: Remove a tag
  ec2_elb_tag:
    name: lb-classroster
    state: absent
    tags:
      LoadTest: passed
  register: task_output

'''

RETURN = '''
load_balancer_name:
    description: name of the balancer acted upon
    returned: success
    type: str
tags:
    description: tags after present/absent/list action
    returned: changed or state:list
    type: list
msg:
    description: user friendly explanation of result
    returned: success
    type: str
'''

try:
    import botocore
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

try:
    import boto
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

class ElbManager:
    """Handles ELB Tagging"""

    def __init__(self, module):
        self.module = module

        try:
            region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
            if not region:
                module.fail_json(msg="Region must be specified as a parameter, in EC2_REGION or AWS_REGION environment variables or in boto configuration file")
            self.elb = boto3_conn(module, conn_type='client', resource='elb', region=region, endpoint=ec2_url, **aws_connect_kwargs)
        except botocore.exceptions.NoCredentialsError, e:
            self.module.fail_json(msg="Can't authorize connection - "+str(e))

    def add_tags(self, balancer_name, tags):
        lbtags = []
        for k in tags.keys():
            lbtags.append({'Key': k, 'Value': tags[k]})

        response = self.elb.add_tags(
            LoadBalancerNames=[balancer_name],
            Tags=lbtags
        )
        return response

    def list_tags(self, balancer_name):
        try:
            response = self.elb.describe_tags(
                LoadBalancerNames=[balancer_name]
                )

            return response['TagDescriptions'][0]['Tags']

        # assume balancer doesn't exist
        except botocore.exceptions.ClientError as e:
            # e['Error']['Message']
            self.module.fail_json(msg="ELB %s not found" % (balancer_name))
            return None

    def remove_tags(self, balancer_name, tags):
        lbtags = []
        for k in tags.keys():
            lbtags.append({'Key': k})

        response = self.elb.remove_tags(
            LoadBalancerNames=[balancer_name],
            Tags=lbtags
        )
        return response

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            name=dict(required=True, type='str'),
            state = dict(default='present', choices=['present', 'absent', 'list']),
            tags=dict(),
        )
    )

    # boto3 ELB client does not support DryRun for tags, do not implement
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    # Validate Requirements
    if not HAS_BOTO3:
      module.fail_json(msg='boto3 is required.')

    elbname = module.params.get('name')
    state = module.params.get('state').lower()
    tags = module.params.get('tags')

    service_mgr = ElbManager(module)

    gettags = service_mgr.list_tags(elbname)

    dictadd = {}
    dictremove = {}
    baddict = {}
    tagdict = {}
    for tag in gettags:
        tagdict[tag['Key']] = tag['Value']

    results = dict(changed=False)

    results['load_balancer_name'] = elbname

    if state == 'present':
        if not tags:
            module.fail_json(msg="tags argument is required when state is present")
        if set(tags.items()).issubset(set(tagdict.items())):
            results['tags'] = gettags
            results['msg'] = "Tags already exists for ELB %s." % elbname
            module.exit_json(**results)
        else:
            for (key, value) in set(tags.items()):
                if (key, value) not in set(tagdict.items()):
                    dictadd[key] = value

        service_mgr.add_tags(elbname, dictadd)
        gettags = service_mgr.list_tags(elbname)

        results['changed'] = True
        results['tags'] = gettags
        results['msg'] = "Tags %s created for ELB %s." % (dictadd,elbname)

    if state == 'absent':
        if not tags:
            module.fail_json(msg="tags argument is required when state is absent")
        for (key, value) in set(tags.items()):
            if (key, value) not in set(tagdict.items()):
                baddict[key] = value
                if set(baddict) == set(tags):
                    results['tags'] = gettags
                    results['msg'] = msg="Nothing to remove here. Move along."
                    module.exit_json(**results)
        for (key, value) in set(tags.items()):
            if (key, value) in set(tagdict.items()):
                dictremove[key] = value

        service_mgr.remove_tags(elbname, dictremove)
        gettags = service_mgr.list_tags(elbname)

        results['changed'] = True
        results['tags'] = gettags
        results['msg'] = "Tags %s removed for ELB %s." % (dictremove,elbname)

    if state == 'list':
        results['tags'] = gettags
        results['msg'] = "Tags listed for ELB %s." % (elbname)

    module.exit_json(**results)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
