import json
import pprint
from xos.config import Config, XOS_DIR
from xos.logger import observer_logger
from tackerclient.client import HTTPClient, construct_http_client
from tackerclient.common.exceptions import Unauthorized, ConnectionFailed
from tackerclient.common.exceptions import SslCertificateValidationError
from requests.exceptions import HTTPError

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
_api_version = 'v1.0'


def get_tacker_client(site, service_type='nfv-orchestration', timeout=None, **kwargs):
    """
    Get a client connection to Tacker authenticated with our Keystone credentials

        ie) client = construct_http_client(username='admin', password='devstack', tenant_name='admin',
                                          auth_url='http://192.168.1.121:5000/v2.0')

    :param site: (ControllerSite) Site to get client for
    :param service_type: (string) Service type defined for Tacker service.  For the Liberty
                                  release, this will may be 'servicevm', for Mitaka+, it will
                                  most likely be 'nfv-orchestration'.  Run the following command
                                  on your controller to verify:  'openstack service list' and
                                  look for the'tacker' entry's 'Type'
    :param timeout: (integer) Connection timeout, see keystoneclient.v2_0.client module

    :return: (HttpClient) Tacker HTTP API client
    """
    observer_logger.info('TACKER: get client request: user: %s, tenant: %s, auth: %s' %
                         (site.controller.admin_user, site.controller.admin_tenant, site.controller.auth_url))

    client = construct_http_client(username=site.controller.admin_user,
                                   tenant_name=site.controller.admin_tenant,
                                   password=site.controller.admin_password,
                                   auth_url=site.controller.auth_url,
                                   service_type=service_type,
                                   timeout=timeout, **kwargs)
    if not client:
        observer_logger.info('TACKER: get client failed')
    else:
        observer_logger.info('TACKER: get client results: %s' % client)

        try:
            client.authenticate()
        except Unauthorized as e:
            observer_logger.error('get_tacker_client: (%s of %s) authentication error: %s' % (site.controller.admin_user,
                                                                                              site.controller.admin_tenant,
                                                                                              e.message))
            raise

        except ConnectionFailed:
            # This can happen during unittest if you retry too often
            raise

    return client


def get_vnfd_list(client):
    """
    Get a list of all installed VNF descriptors

        ie) client.do_request(url='/v1.0/vnfds', method='GET')
            (<Response [200]>,
            u'{"vnfds":
                [
                    {
                        "service_types": [
                            {
                                "service_type": "vnfd",
                                "id": "b3f31224-8f94-4e8f-b08c-0004b77d22b8"
                            }
                        ],
                        "description": "FreeRADIUS Server",
                        "tenant_id": "092e0614241941568b4c0e6406f7c28f",
                        "mgmt_driver": "noop",
                        "infra_driver": "heat",
                        "attributes": {
                            "vnfd": "tosca_definitions_version: ... <tosca-file-content> ..."
                        },
                        "id": "89b1b3c1-7a88-476b-a13e-9ec49991ab30",
                        "name": "RADIUS Server"
                    },
                    ...
                ]
            }')

    :param client: (HttpClient) Tacker HTTP API client

    :return: (list of dicts) Installed VNF descriptors
    """

    try:
        response = client.do_request(url='/%s/vnfds' % _api_version, method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('get_vnfd_list: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                             client.tenant_name,
                                                                                             e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('get_vnfd_list: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                         client.tenant_name,
                                                                                         e.message))
        raise

    # Response is a tuple with [0] -> class 'requests.models.response'
    # Check response status
    try:
        response[0].raise_for_status()

    except HTTPError as e:
        observer_logger.error('get_vnfd_list: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    return response[0].json()['vnfds']


def get_nfvd(client, vnfd_id):
    """
    Get an installed VNF descriptor

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

    :param client:  (HttpClient) Tacker HTTP API client
    :param nfvd_id: (string) VNF ID (UUID) to retrieve

    :return: (dict) Installed VNF descriptor or None on failure
    """

    try:
        response = client.do_request(url='%s/vnfds/%s' % (_api_version, vnfd_id), method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('get_vnfd: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('get_vnfd: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                    client.tenant_name,
                                                                                    e.message))
        raise

    # Check response status
    try:
        response.raise_for_status()

    except HTTPError as e:
        observer_logger.error('get_vnfd: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                   client.tenant_name,
                                                                                   e.message))
        raise

    json_data = response[0].json()['vnfd']

    return json_data if len(json_data) > 0 else None


def onboard_vnfd(client, filename, vnfd_name=None, vnfd_description=None, username=None, password=None, tenant_name=None):
    """
    Install VNFD

    ie)     client.do_request(url='/v1.0/vnfds', method='POST')
            request args = {
                "auth": {"tenantName": "admin",
                         "passwordCredentials": {"username": "admin", "password": "devstack"}},
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
                    "service_types": [ { "service_type": "vnfd" } ],
                    "mgmt_driver": "noop",
                    "infra_driver": "heat"
                }
            }
            response =  {
                "vnfd": {
                    "service_types": [
                        {
                            "service_type": "vnfd",
                            "id": "336fe422-9fba-47c7-87fb-d48475c3e0ce"
                        }
                    ],
                    "description": "OpenWRT router",
                    "tenant_id": "4dd6c1d7b6c94af980ca886495bcfed0",
                    "mgmt_driver": "noop",
                    "infra_driver": "heat",
                    "attributes": {
                        "vnfd": "template_name: OpenWRT \r\ndescription:
                        template_description <sample_vnfd_template>"
                    },
                    "id": "ab10a543-22ee-43af-a441-05a9d32a57da",
                    "name": "OpenWRT"
                }
            }

    :param client: (HttpClient) Tacker HTTP API client
    :param filename: (string) VNFD TOSCA File/Template
    :param vnfd_name: (string) Name to give newly created VNFD
    :param vnfd_description: (string) VNFD Description text
    :param username: (string) Authentication username to use
    :param password: (string) Authentication password
    :param tenant_name: (string) Default tenant name (or UUID) to launch VNFs in     TODO: Verify this param

    :return: (tuple) (name, UUID of installed VNFD) if successful
    """

    auth = {
        'passwordCredentials':
            {
                'username': username if username is not None else client.username,
                'password': password if password is not None else client.password
            }
    }
    if tenant_name is None:
        auth['tenant_id'] = client.get_auth_info()['auth_tenant_id']
    else:
        auth['tenant_name'] = tenant_name

    # TODO: How do we give it a specific VNFD name ????
    # TODO: Need a lot of testing on this function.  Look into error returns if parsing fails
    # TODO: Look into TOSCA parser file differences between Libery & Mitaka.  Make Mitaka work first !
    # VNFD portion

    with open(filename) as f:
        tosca = f.read()

    vnfd = {'attributes': {'vnfd': tosca},
            'service_types': [{'service_type': 'vnfd'}],
            'mgmt_driver': 'noop',
            'infra_driver': 'heat'}

    if vnfd_name is not None:
        vnfd['name'] = vnfd_name

    if vnfd_description is not None:
        vnfd['description'] = vnfd_description

    body = {'auth': auth, 'vnfd': vnfd}

    # TODO: May want to add parameter  'ensure_ascii=False' to json.dumps below
    json_body = json.dumps(body)

    try:
        # pprint.PrettyPrinter(indent=4).pprint(json_body)
        response = client.do_request(url='%s/vnfds' % _api_version, method='POST',
                                     body=json_body)

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('onboard_vnfd: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                            client.tenant_name,
                                                                                            e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('onboard_vnfd: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    # Check response status
    try:
        # print 'Response type is %s' % type(response)        # Tuple
        # print 'Response[0] type is %s' % type(response[0])  # requests.modes.Response
        pprint.PrettyPrinter(indent=4).pprint(response)
        response.raise_for_status()

    except HTTPError as e:
        observer_logger.error('onboard_vnfd: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                       client.tenant_name,
                                                                                       e.message))
        raise

    return response[0].json()['name'], response[0].json()['id']


def destroy_nfvd(client, vnfd_id):
    """
    Delete a given VNFD from the catalog
    :param client: (HttpClient) Tacker HTTP API client
    :param vnfd_id: (string) VNFD UUID
    :return: True if successful
    """
    try:
        response = client.do_request(url='%s/vnfd/%s' % (_api_version, vnfd_id), method='DELETE')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('destroy_nfvd: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                            client.tenant_name,
                                                                                            e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('destroy_nfvd: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    # TODO: Debug this.
    # Check response status
    try:
        response[0].raise_for_status()

    except HTTPError as e:
        observer_logger.error('destroy_nfvd: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                       client.tenant_name,
                                                                                       e.message))
        raise

    return True


def get_vnf_list(client):
    """
    Get a list of all running VNFs

        ie) client.do_request(url='/v1.0/vnfs', method='GET')
            (<Response [200]>, u'{"vnfs": []}')

    :param client: (HttpClient) Tacker HTTP API client

    :return: (list of dicts) Current list of NFVs
    """

    try:
        response = client.do_request(url='%s/vnfs' % _api_version, method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('get_vnf_list: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                            client.tenant_name,
                                                                                            e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('get_vnf_list: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    # Response is a tuple with [0] -> class 'requests.models.response'
    # Check response status
    try:
        response[0].raise_for_status()

    except HTTPError as e:
        observer_logger.error('get_vnf_list: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                       client.tenant_name,
                                                                                       e.message))
        raise

    return response[0].json()['vnfs']


def get_vnf(client, vnf_id):
    """
    Get a list of all running NFVs

    GET /v1.0/vnfs

        ie) client.do_request(url='/v1.0/vnfs/{id}', method='GET')
            (<Response [200]>, u'{"vnfs": []}')

    :param client: (HttpClient) Tacker HTTP API client
    :param vnf_id: (string) UUID of VNF to retrieve

    :return: (list of dicts) Current list of NFVs
    """

    try:
        response = client.do_request(url='%s/vnfs/%s' % (_api_version, vnf_id), method='GET')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('get_nfv_list: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                            client.tenant_name,
                                                                                            e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('get_nfv_list: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                        client.tenant_name,
                                                                                        e.message))
        raise

    # Response is a tuple with [0] -> class 'requests.models.response'
    # Check response status
    try:
        response[0].raise_for_status()

    except HTTPError as e:
        observer_logger.error('get_nfv_list: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                       client.tenant_name,
                                                                                       e.message))
        raise

    # TODO: Debug this. Document says this is a list of dict (with 1 item) but that does not make sense
    json_data = response[0].json()['vnf']

    return json_data if len(json_data) > 0 else None


def launch_nfv(client, vnfd_id, param_filename, username=None, password=None, tenant_name=None):
    """
    Launch an VNF

    PUT /v1.0/vnfs/{vnf_id}

    Request:
      {
        "auth": {"tenantName": "admin",
                 "passwordCredentials": {"username": "admin", "password": "devstack"}},
        "vnf": {"vnfd_id": "d770ddd7-6014-4191-92d8-a2cd7a6cecd8"}}

    Response:
        {
            "vnf": {
                "status": "PENDING_CREATE",
                "name": "",
                "tenant_id": "4dd6c1d7b6c94af980ca886495bcfed0",
                "description": "OpenWRT with services",
                "instance_id": "4f0d6222-afa0-4f02-8e19-69e7e4fd7edc",
                "mgmt_url": null,
                "attributes": {
                    "service_type": "firewall",
                    "heat_template": "description: OpenWRT with services\n
                    <sample_heat_template> type: OS::Nova::Server\n",
                    "monitoring_policy": "noop",
                    "failure_policy": "noop"
                },
                "id": "e3158513-92f4-4587-b949-70ad0bcbb2dd",
                "vnfd_id": "247b045e-d64f-4ae0-a3b4-8441b9e5892c"
            }
        }

    :param client: (HttpClient) Tacker HTTP API client
    :param vnfd_id: (string) VNF UUID
    :param param_filename: Filename of VNFD template parameters, if any
    :param username: (string) Authentication username to use
    :param password: (string) Authentication password
    :param tenant_name: (string) Default tenant name (or UUID) to launch VNFs in     TODO: Verify this param

    :return: (dict) VNF launch results (see 'vnf' dict contents above for example)
    """
    if tenant_name is None:
        tenant_name = client.get_auth_info()['auth_tenant_id']

    auth = {
        'tenantName': tenant_name,
        'passwordCredentials':
            {
                'username': username if username is not None else client.username,
                'password': password if password is not None else client.password
            }
    }
    # TODO: How do we give it a specific VNF name ????
    # TODO: What about multi-VIM support in Mitaka+

    # VNF portion

    vnf = {'vnfd_id': vnfd_id}

    # TODO: How is a parameter file passed in.  May be this way
    # TODO: Also support a config file,  see .../python-tackerclinet/tackerclient/tacker/v1_0/vm/vnf.py

    if param_filename is not None:
        with open(param_filename) as f:
            vnf['attributes']['param_values'] = f.read()

    # Create body for request

    body = {'auth': auth, 'vnf': vnf}

    # TODO: May want to add parameter  'ensure_ascii=False' to json.dumps below
    json_body = json.dumps(body)

    try:
        response = client.do_request(url='%s/vnfs' % _api_version, method='POST',
                                     body=json_body)

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('launch_nfv: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                          client.tenant_name,
                                                                                          e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('launch_nfv: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                      client.tenant_name,
                                                                                      e.message))
        raise

    # Check response status
    try:
        response.raise_for_status()

    except HTTPError as e:
        observer_logger.error('launch_nfv: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                     client.tenant_name,
                                                                                     e.message))
        raise

    return response[0].json()['vnf']


def update_nfv(client, vnf_id, config_filename, username=None, password=None, tenant_name=None):
    """
    Update a vnf based on user config file or data.

    PUT /v1.0/vnfs/{vnf_id}

    Request:
        {"auth": {"tenantName": "admin",
                  "passwordCredentials": {"username": "admin", "password": "devstack"}},
        "vnf": {"attributes": {"config": "vdus:\n  vdu1: <sample_vdu_config> \n\n"}}}

    Response:
        {
            "vnf": {
                "status": "PENDING_UPDATE",
                "name": "",
                "tenant_id": "4dd6c1d7b6c94af980ca886495bcfed0",
                "instance_id": "4f0d6222-afa0-4f02-8e19-69e7e4fd7edc",
                "mgmt_url": "{\"vdu1\": \"192.168.120.4\"}",
                "attributes": {
                    "service_type": "firewall",
                    "monitoring_policy": "noop",
                    "config": "vdus:\n  vdu1:\n    config: {<sample_vdu_config>
                     type: OS::Nova::Server\n",
                    "failure_policy": "noop"
                },
                "id": "e3158513-92f4-4587-b949-70ad0bcbb2dd",
                "description": "OpenWRT with services"
            }
        }


    :param client: (HttpClient) Tacker HTTP API client
    :param vnf_id: (string) VNF UUID
    :param config_filename: Configuration filename
    :param username: (string) Authentication username to use
    :param password: (string) Authentication password
    :param tenant_name: (string) Default tenant name (or UUID) to launch VNFs in     TODO: Verify this param


    :return: (dict) VNF launch results (see 'vnf' dict contents above for example)
    """
    if tenant_name is None:
        tenant_name = client.get_auth_info()['auth_tenant_id']

    auth = {
        'tenantName': tenant_name,
        'passwordCredentials':
            {
                'username': username if username is not None else client.username,
                'password': password if password is not None else client.password
            }
    }
    config = {}
    with open(config_filename) as f:
        config['attributes']['config'] = f.read()

    # Create body for request

    body = {'auth': auth, 'vnf': config}

    # TODO: May want to add parameter  'ensure_ascii=False' to json.dumps below
    json_body = json.dumps(body)

    try:
        response = client.do_request(url='%s/vnfs' % _api_version, method='POST',
                                     body=json_body)

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('update_nfv: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                          client.tenant_name,
                                                                                          e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('update_nfv: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                      client.tenant_name,
                                                                                      e.message))
        raise

    # Check response status
    try:
        response.raise_for_status()

    except HTTPError as e:
        observer_logger.error('update_nfv: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                     client.tenant_name,
                                                                                     e.message))
        raise

    return response[0].json()['vnf']


def destroy_nfv(client, vnf_id):
    """
    Stop and delete a given VNF
    :param client: (HttpClient) Tacker HTTP API client
    :param vnf_id: (string) VNF UUID
    :return: True if successful
    """
    try:
        response = client.do_request(url='%s/vnfs/%s' % (_api_version, vnf_id), method='DELETE')

    except (Unauthorized, SslCertificateValidationError) as e:
        observer_logger.error('destroy_nfv: Client (%s of %s) authentication error: %s' % (client.username,
                                                                                           client.tenant_name,
                                                                                           e.message))
        raise

    except ConnectionFailed as e:
        observer_logger.error('destroy_nfv: Client (%s of %s) Connection error: %s' % (client.username,
                                                                                       client.tenant_name,
                                                                                       e.message))
        raise

    # Response is a tuple with [0] -> class 'requests.models.response'
    # Check response status
    try:
        response[0].raise_for_status()

    except HTTPError as e:
        observer_logger.error('destroy_nfv: Client (%s of %s) Response Failed: %s' % (client.username,
                                                                                      client.tenant_name,
                                                                                      e.message))
        raise

    # TODO: Debug this.
    return True
