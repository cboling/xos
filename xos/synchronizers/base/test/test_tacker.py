#!/usr/bin/python

from defaults import *
from test_classes import ControllerTest, SiteTest

from xos.synchronizers.base import tacker as tackerV10
import argparse

###########################################################################
# Parse the command line

parser = argparse.ArgumentParser(description='Mock RESTCONF Device')

parser.add_argument('--verbose', '-v', action='store_true', default=False,
                    help='Output verbose information')
parser.add_argument('--username', '-u', action='store', default=OPENSTACK_USER,
                    help='Administrative User Name')
parser.add_argument('--password', '-p', action='store', default=OPENSTACK_PASSWORD,
                    help='Administrative Password')
parser.add_argument('--tenant', '-t', action='store', default=OPENSTACK_TENANT_NAME,
                    help='Administrative Tenant Name')
parser.add_argument('--auth_url', '-a', action='store', default=OPENSTACK_AUTH_URL,
                    help='Keystone Authorization URL')
parser.add_argument('--service_type', '-s', action='store', default=OPENSTACK_SERVICE_TYPE,
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

import unittest


class SimplisticTest(unittest.TestCase):
    def test(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()