import jinja2
import tempfile
import os
import string
from xos.config import Config, XOS_DIR
from xos.logger import observer_logger
from tackerclient.client import HTTPClient, construct_http_client
from tackerclient.common.exceptions import Unauthorized, ConnectionFailed
from tackerclient.common.exceptions import SslCertificateValidationError

try:
    step_dir = Config().observer_steps_dir
    sys_dir = Config().observer_sys_dir
except:
    step_dir = XOS_DIR + '/synchronizers/openstack/steps'
    sys_dir = '/opt/opencloud'

# Tacker API version to use.  Note you can also use an authenticated client and perform:
#    client.do_request(url='/', method='GET')
#    (<Response [200]>,
#         u'{"versions": [{"status": "CURRENT", "id": "v1.0",
#                                "links": [{"href": "http://192.168.1.121:8888/v1.0", "rel": "self"}]}]}')
#
# If you want to programatically look for a different version that you have coded to.  Currently only V1.0 of
# the Tacker API exists.
#
#         See: http://tacker-docs.readthedocs.io/en/latest/devref/mano_api.html
#
_api_version = '1.0'


def get_tacker_client(site, timeout=None):
    """
    Get a client connection to Tacker authenticated with our Keystone credentials


        ie) client = construct_http_client(username='admin', password='devstack', tenant_name='admin',
                                          auth_url='http://192.168.1.121:5000/v2.0')

    :param site: (ControllerSite) Site to get client for
    :param timeout: (integer) Connection timeout, see keystoneclient.v2_0.client module

    :return: (HttpClient) Tacker HTTP API client
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

        try:
            client.authenticate();
        except Unauthorized as e:
            observer_logger.error('Client (%s of %s) authentication error: %s' % (site.controller.admin_user,
                                                                                  site.controller.admin_tenant,
                                                                                  e.message))
            raise

    return client


def get_nfvd_list(client, filter=None):
    """
    Get a list of all installed NFV descriptors

        ie) client.do_request(url='/v1.0/vnfds', method='GET')
            (<Response [200]>, u'{"vnfds": []}')

    :param client: (HttpClient) Tacker HTTP API client
    :param filter: (string) Optional attributes

    :return: (list of dicts) Installed NFV descriptors
    """

    try:
        response = client.do_request(url='%s/vnfds' % _api_version, method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('Client (%s of %s) authentication error: %s' % (client.username,
                                                                              client.tenant_name,
                                                                              e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('Client (%s of %s) Connection error: %s' % (client.username,
                                                                          client.tenant_name,
                                                                          e.message))
        raise

    # TODO: error/response code check

    if filter:
        # TODO, apply filters...
        pass

    return response.vnfds


def get_nfvd(client, id):
    """
    Get an installed NFV descriptor

        ie) client.do_request(url='/v1.0/vnfds/378b774d-89f5-4634-9c65-9c49ed6f00ce', method='GET')
            (<Response [200]>,
            u'{ "vnfd": {
                    "service_types": [
                        {
                            "service_type": "vnfd",
                            "id": "378b774d-89f5-4634-9c65-9c49ed6f00ce"
                        }
                    ],
                    "description": "OpenWRT with services",
                    "tenant_id": "4dd6c1d7b6c94af980ca886495bcfed0",
                    "mgmt_driver": "openwrt",
                    "infra_driver": "heat",
                    "attributes": {
                        "vnfd": "template_name: OpenWRT\r\ndescription:
                        template_description <sample_vnfd_template>"
                    },
                    "id": "247b045e-d64f-4ae0-a3b4-8441b9e5892c",
                    "name": "openwrt_services"
                }
            }')

    :param client: (HttpClient) Tacker HTTP API client
    :param id:     (string) VNF ID (UUID) to retrive

    :return: (dicts) Installed NFV descriptor or None on failure
    """

    try:
        response = client.do_request(url='%s/vnfds' % _api_version, method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('Client (%s of %s) authentication error: %s' % (client.username,
                                                                              client.tenant_name,
                                                                              e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('Client (%s of %s) Connection error: %s' % (client.username,
                                                                          client.tenant_name,
                                                                          e.message))
        raise

    # TODO: error/response code check.  What does it return on 'not found'

    return response.vnfd


def onboard_nfvd(client, file, name):
    """
    Install NFVD

    ie)     client.do_request(url='/v1.0/vnfd', method='POST')
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


    :param client: (HttpClient) Tacker HTTP API client
    :param file: (string) VNFD TOSCA File/Template
    :param name:
    :return: UUID of installed NFVc if successful
    """
    pass

def get_nfv_list(client, filter=None):
    """
    Get a list of all running NFVs

        ie) client.do_request(url='/v1.0/vnfs', method='GET')
            (<Response [200]>, u'{"vnfs": []}')

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