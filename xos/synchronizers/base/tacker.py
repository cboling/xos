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