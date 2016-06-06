import jinja2
import tempfile
import os
import string
from xos.config import Config, XOS_DIR
from xos.logger import observer_logger
from tackerclient.client import HTTPClient, construct_http_client

try:
    step_dir = Config().observer_steps_dir
    sys_dir = Config().observer_sys_dir
except:
    step_dir = XOS_DIR + '/synchronizers/openstack/steps'
    sys_dir = '/opt/opencloud'


def get_tacker_client(site, timeout=None):
    """
    Get a client connection to Tacker
    :param site: (ControllerSite) Site to get client for
    :param timeout: (integer) Connection timeout, see keystoneclient.v2_0.client module
    :return: (HttpClient) Tacker HTTP API client

    Here is example from CLI.  See http://tacker-docs.readthedocs.io/en/latest/devref/mano_api.html

    client = construct_http_client(username='admin', password='devstack',
                tenant_name='admin', auth_url='http://192.168.1.121:5000/v2.0')

>>> client.get_auth_info()
{'auth_token': None, 'auth_user_id': None, 'auth_tenant_id': None, 'endpoint_url': None}
>>> client.authenticate()
>>> client.get_auth_info()
{'auth_token': u'96a37b6856bc45b4b6ff7b7afdd223b0', 'auth_user_id': u'eacb1a618ff341d5a444fcfb0487e7ea', 'auth_tenant_id': u'46f4d2e73b9749b0a528508abc61d03e', 'endpoint_url': u'http://192.168.1.121:8888/'}


>>>
>>> client.do_request(url='/', method='GET')
(<Response [200]>, u'{"versions": [{"status": "CURRENT", "id": "v1.0", "links": [{"href": "http://192.168.1.121:8888/v1.0", "rel": "self"}]}]}')
>>>
KeyboardInterrupt
>>>
>>> client.do_request(url='/v1.0/vnfds', method='GET')
(<Response [200]>, u'{"vnfds": []}')
>>>
>>>
>>>
>>> client.do_request(url='/v1.0/vnfs', method='GET')
(<Response [200]>, u'{"vnfs": []}')

args = {
    "auth": { "tenantName": "admin", "passwordCredentials": { "username": "admin", "password": "devstack" } },
    "vnfd": {
        "attributes": {
            "vnfd": "template_name:
            OpenWRT \r\ndescription: OpenWRT router\r\n\r\nservice_properties:\r\n  Id:
            sample-vnfd\r\n  vendor: tacker\r\n  version: 1\r\n\r\nvdus:\r\n  vdu1:\r\n
            id: vdu1\r\n    vm_image: cirros-0.3.2-x86_64-uec\r\n    instance_type:
            m1.tiny\r\n\r\n    network_interfaces:\r\n      management:\r\n        network:
            net_mgmt\r\n        management: true\r\n      pkt_in:\r\n        network:
            net0\r\n      pkt_out:\r\n        network: net1\r\n\r\n    placement_policy:
            \r\n      availability_zone: nova\r\n\r\n    auto-scaling: noop\r\n
            monitoring_policy: noop\r\n    failure_policy: noop\r\n\r\n    config:\r\n
            param0: key0\r\n      param1: key1"
        },
        "service_types": [
            {
                "service_type": "vnfd"
            }
        ],
        "mgmt_driver": "noop",
        "infra_driver": "heat"
    }
}




    """
    observer_logger.info('TACKER: get client request: user: %s, tenant: %s, auth: %s' %
                         (site.controller.admin_user, site.controller.admin_tenant, site.controller.auth_url))

    client = construct_http_client(username=site.controller.admin_user,
                                   tenant_name=site.controller.admin_tenant,
                                   password=site.controller.admin_password,
                                   auth_url=site.controller.auth_url,
                                   timeout=timeout)
    if not client:
        observer_logger.info('TACKER: get client failed')
    else:
        observer_logger.info('TACKER: get client results: %s' % client)
    pass

def get_nfvd_list(client, filter=None):
    """
    Get a list of all installed NFV descriptors
    :param client: (HttpClient) Tacker HTTP API client
    :param filter: (string) Optional NFVD name to filter on
    :return: (list of dicts) Installed NFV descriptors
    """
    pass

def onboard_nfvd(client, file, name):
    """
    Install NFVD
    :param client: (HttpClient) Tacker HTTP API client
    :param file:
    :param name:
    :return: UUID of installed NFVc if successful
    """
    pass

def get_nfv_list(client, filter=None):
    """
    Get a list of all running NFVs
    :param client: (HttpClient) Tacker HTTP API client
    :param filter: (string) Optional NFVD name to filter on
    :return: (list of dicts) Current list of NFVs
    """
    pass

def launch_nfv(client, nfvd, params):
    """
    Launch an NFV
    :param client: (HttpClient) Tacker HTTP API client
    :param nfvd:
    :param params:
    :return: UUID of installed NFV if successful
    """
    pass

def destroy_nfv(client, nfv):
    """
    Stop NFV
    :param client: (HttpClient) Tacker HTTP API client
    :param nfv: (string) name
    :return: True if successful
    """
    pass