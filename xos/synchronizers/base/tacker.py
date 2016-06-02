import jinja2
import tempfile
import os
import string
from xos.config import Config, XOS_DIR
from xos.logger import observer_logger
#from tackerclient.client import *

try:
    step_dir = Config().observer_steps_dir
    sys_dir = Config().observer_sys_dir
except:
    step_dir = XOS_DIR + '/synchronizers/openstack/steps'
    sys_dir = '/opt/opencloud'


def get_tacker_client(site):
    """
    Get a client connection to Tacker
    :param site:
    :return: (Client) Tacker client
    """
    pass

def get_nfvd_list(client, filter=None):
    """
    Get a list of all installed NFV descriptors
    :param client: (Client) Tacker client
    :param filter: (String) Optional NFVD name to filter on
    :return: (list of dicts) Installed NFV descriptors
    """
    pass

def onboard_nfvd(client, file, name):
    """
    Install NFVD
    :param client:
    :param file:
    :param name:
    :return: UUID of installed NFVc if successful
    """
    pass

def get_nfv_list(client, filter=None):
    """
    Get a list of all running NFVs
    :param client:
    :param filter: (String) Optional NFVD name to filter on
    :return: (list of dicts) Current list of NFVs
    """
    pass

def launch_nfv(client, nfvd, params):
    """
    Launch an NFV
    :param client:
    :param nfvd:
    :param params:
    :return: UUID of installed NFV if successful
    """
    pass

def destroy_nfv(client, nfv):
    """
    Stop NFV
    :param client:
    :param nfv: (string) name
    :return: True if successful
    """
    pass