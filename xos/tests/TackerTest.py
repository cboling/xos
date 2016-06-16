#!/usr/bin/python

from xos.synchronizers.base import tacker as tackerV10
import argparse

_TACKER_VNFD_YAML = 'files/cirros-mitaka.yaml'               # No parameters
_TACKER_VNFD_TEMPLATE = 'files/radius-mitaka-template.yaml'  # Takes parameters
_TACKER_VNF_PARAMETERS = 'files/radius-param.yaml'           # VNF template
_TACKER_VNF_CONFIG = 'files/radius-config.yaml'              # Config for VNF launch
_TACKER_VNF_UPDATE = 'files/radius-update.yaml'              # VNF configuration update


class ControllerTest:
    def __init__(self, user, password, tenant, auth_url):
        self.admin_user = user
        self.admin_password = password
        self.admin_tenant = tenant
        self.auth_url = auth_url


class SiteTest:
    def __init__(self, user, password, tenant, auth_url):
        self.controller = ControllerTest(user, password, tenant, auth_url)


###########################################################################
# Parse the command line

parser = argparse.ArgumentParser(description='Mock RESTCONF Device')

parser.add_argument('--verbose', '-v', action='store_true', default=False,
                    help='Output verbose information')
parser.add_argument('--username', '-u', action='store', default='admin',
                    help='Administrative User Name')
parser.add_argument('--password', '-p', action='store', default='devstack',
                    help='Administrative Password')
parser.add_argument('--tenant', '-t', action='store', default='admin',
                    help='Administrative Tenant Name')
parser.add_argument('--auth_url', '-a', action='store', default='http://localhost:35357/v2.0',
                    help='Keystone Authorization URL')
parser.add_argument('--service_type', '-s', action='store', default='nfv-orchestration',
                    help='Service Type for Tacker')

args = parser.parse_args()


def _vnfd_tests(client):
    pass


def _vnf_tests(client):
    pass


#
# Start the tests
#
if __name__ == "__main__":
    # Set up fake site/controller object to use

    mySite = SiteTest(args.username, args.password, args.tenant, args.auth_url)

    if args.verbose:
        print('Creating Tacker HTTP Client')

    try:
        client = tackerV10.construct_http_client(mySite, service_type=args.service_type)

        # First tests VNFD interfaces

        _vnf_tests(client)

        # VNF tests last

        _vnf_tests(client)

        # If here, all tests pass

        print 'Completed all tests as expected'

    except Exception as e:
        print 'Unexpected exception during test run: %s' % e
        raise
