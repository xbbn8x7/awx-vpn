#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright 2018 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: panos_bgp_auth
short_description: Configures a BGP Authentication Profile
description:
    - Use BGP to publish and consume routes from disparate networks.
author:
    - Joshua Colson (@freakinhippie)
    - Garfield Lee Freeman (@shinmog)
version_added: '1.0.0'
requirements:
    - pan-python can be obtained from PyPI U(https://pypi.python.org/pypi/pan-python)
    - pandevice can be obtained from PyPI U(https://pypi.python.org/pypi/pandevice)
notes:
    - Checkmode is not supported.
    - Panorama is supported.
    - Since the I(secret) value is encrypted in PAN-OS, there is no way to verify
      if the secret is properly set or not.  Invoking this module with I(state=present)
      will always apply the config to PAN-OS.
extends_documentation_fragment:
    - paloaltonetworks.panos.fragments.transitional_provider
    - paloaltonetworks.panos.fragments.state
    - paloaltonetworks.panos.fragments.full_template_support
    - paloaltonetworks.panos.fragments.deprecated_commit
options:
    name:
        description:
            - Name of Authentication Profile.
        type: str
        required: True
    replace:
        description:
            - B(Deprecated)
            - This is the behavior of I(state=present), so this can safely be removed from your playbooks.
            - HORIZONTALLINE
            - The secret is encrypted so the state cannot be compared.
            - This option forces removal of a matching item before applying the new config.
        type: bool
    secret:
        description:
            - Secret.
        type: str
    vr_name:
        description:
            - Name of the virtual router, it must already exist.  See M(panos_virtual_router).
        type: str
        default: 'default'
'''

EXAMPLES = '''
- name: Create BGP Authentication Profile
  panos_bgp_auth:
    provider: '{{ provider }}'
    vr_name: 'my virtual router'
    name: auth-profile-1
    secret: SuperSecretCode
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.paloaltonetworks.panos.plugins.module_utils.panos import get_connection

try:
    from panos.errors import PanDeviceError
    from panos.network import Bgp
    from panos.network import BgpAuthProfile
    from panos.network import VirtualRouter
except ImportError:
    try:
        from pandevice.errors import PanDeviceError
        from pandevice.network import Bgp
        from pandevice.network import BgpAuthProfile
        from pandevice.network import VirtualRouter
    except ImportError:
        pass


def setup_args():
    return dict(
        commit=dict(type='bool', default=False),
        vr_name=dict(default='default'),
        replace=dict(type='bool'),
        name=dict(type='str', required=True),
        secret=dict(type='str', no_log=True),
    )


def main():
    helper = get_connection(
        template=True,
        template_stack=True,
        with_state=True,
        with_classic_provider_spec=True,
        argument_spec=setup_args(),
    )

    module = AnsibleModule(
        argument_spec=helper.argument_spec,
        supports_check_mode=True,
        required_one_of=helper.required_one_of,
    )

    parent = helper.get_pandevice_parent(module)

    # TODO(gfreeman) - removed in 2.12
    if module.params['replace'] is not None:
        module.deprecate(
            'Param "replace" is deprecated; please remove it from your playbooks',
            version='3.0.0', collection_name='paloaltonetworks.panos'
        )

    vr = VirtualRouter(module.params['vr_name'])
    parent.add(vr)
    try:
        vr.refresh()
    except PanDeviceError as e:
        module.fail_json(msg='Failed refresh: {0}'.format(e))

    bgp = vr.find('', Bgp)
    if bgp is None:
        module.fail_json(msg='BGP config not yet added to {0}'.format(vr.name))
    parent = bgp

    listing = parent.findall(BgpAuthProfile)

    commit = module.params['commit']

    spec = {
        'name': module.params['name'],
        'secret': module.params['secret'],
    }
    obj = BgpAuthProfile(**spec)
    parent.add(obj)

    changed, diff = helper.apply_state(obj, listing, module)

    if commit and changed:
        helper.commit(module)

    module.exit_json(changed=changed, diff=diff, msg='done')


if __name__ == '__main__':
    main()
