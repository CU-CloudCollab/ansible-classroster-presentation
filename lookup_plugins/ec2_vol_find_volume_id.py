# (c) 2015, Eric Grysko <eric@ericgrysko.com>
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2.exceptions import UndefinedError
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms

class LookupModule(LookupBase):

    def _lookup_variables(self, terms, variables):
        results = []
        for x in terms:
            try:
                intermediate = listify_lookup_plugin_terms(x, templar=self._templar, loader=self._loader, fail_on_undefined=True)
            except UndefinedError as e:
                raise AnsibleUndefinedVariable("One of the nested variables was undefined. The error was: %s" % e)
            results.append(intermediate)
        return results

    def run(self, terms, variables=None, **kwargs):

        terms = self._lookup_variables(terms, variables)

        volumes = terms[0]
        device_name = terms[1]

        for volume in volumes:
            attachment_set = volume['attachment_set']
            if [attachment_set['device']] == device_name:
               return [volume['id']]

        raise AnsibleError("device_name '%s' not found in volumes" % device_name)
