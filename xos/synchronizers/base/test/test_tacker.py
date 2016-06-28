#!/usr/bin/python

import unittest
from defaults import *
from TackerTestClasses import SiteTest
from synchronizers.base import tacker
from tackerclient.client import HTTPClient, construct_http_client
from tackerclient.common.exceptions import Unauthorized, ConnectionFailed
from keystoneclient.exceptions import EndpointNotFound
from tackerclient.common.exceptions import SslCertificateValidationError
from requests.exceptions import HTTPError

import sys
import pdb
import functools
import traceback


def debug_on(*exceptions):
    if not exceptions:
        exceptions = (AssertionError, )

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                info = sys.exc_info()
                traceback.print_exception(*info)
                pdb.post_mortem(info[2])
        return wrapper
    return decorator

# These credentials from 'defaults.py' can be assigned on the command line via argparse
_test_credentials = {
    'user': OPENSTACK_USER,
    'password': OPENSTACK_PASSWORD,
    'tenant': OPENSTACK_TENANT_NAME,
    'service_type': OPENSTACK_SERVICE_TYPE,
    'auth_url': 'http://172.22.8.227:35357/v2.0',      # Some various configs for testing,
    # 'auth_url': OPENSTACK_AUTH_URL,
}


def _create_site(user=_test_credentials['user'],
                 password=_test_credentials['password'],
                 tenant=_test_credentials['tenant'],
                 auth_url=_test_credentials['auth_url']):
    """
    Create an XOS equivalent 'Site' to use during tests
    :param user: (string) Username
    :param password: (string) Password
    :param tenant: (string) OpenStack tenant/project
    :param auth_url: (string) Keystone authorization URL
    :return: An XOS equivalent 'Site' object
    """
    return SiteTest(user=user,
                    password=password,
                    tenant=tenant,
                    auth_url=auth_url)


def _create_client(user=_test_credentials['user'],
                   password=_test_credentials['password'],
                   tenant=_test_credentials['tenant'],
                   auth_url=_test_credentials['auth_url'],
                   service_type=_test_credentials['service_type'],
                   **kwargs):
    """
    Create a Tacker client to use during Tacker API calls
    :param user: (string) Username
    :param password: (string) Password
    :param tenant: (string) OpenStack tenant/project
    :param auth_url: (string) Keystone authorization URL
    :param service_type: (string) Service type defined for Tacker service.  For the Liberty
                                  release, this will may be 'servicevm', for Mitaka+, it will
                                  most likely be 'nfv-orchestration'.  Run the following command
                                  on your controller to verify:  'openstack service list' and
                                  look for the'tacker' entry's 'Type'
    :param kwargs:
    :return: Tacker client

    TODO: Change return argument to an object with methods that are the API calls into tacker
    """
    return tacker.get_tacker_client(_create_site(user=user,
                                                 password=password,
                                                 tenant=tenant,
                                                 auth_url=auth_url),
                                    service_type=service_type,
                                    **kwargs)


def _onboard_vnfd(client, vnfd_file):
    """
    Onboard a known good VNFD
    :param client:
    :param vnfd_file:
    :return:
    """
    pass


class CredentialsTest(unittest.TestCase):
    @debug_on()
    def setUp(self):
        self.client = _create_client()

    def tearDown(self):
        self.client = None

    @debug_on()
    def testClientLogin(self):
        """Verify our credentials are valid"""
        self.assertTrue(self.client is not None)
        self.assertIsInstance(self.client, HTTPClient)

    @debug_on()
    def testClientLoginExtras(self):
        """Verify additional arguments can be passed on all the way to the openstack call"""

        # Just pass in existing defaults for some of the extra parameters to the Tacker
        # construct_http_client() API call
        # TODO: later may want more than just defaults in the tests below

        extra_client = _create_client(endpoint_url=None)
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

        extra_client = _create_client(insecure=False)
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

        extra_client = _create_client(auth_strategy='keystone')
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

        extra_client = _create_client(ca_cert=None)
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

        extra_client = _create_client(log_credentials=False)
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

        extra_client = _create_client(endpoint_type='publicURL')
        self.assertTrue(extra_client is not None)
        self.assertIsInstance(extra_client, HTTPClient)

    @debug_on()
    def testInvalidClientLoginUser(self):
        """Verify bad credentials are not valid and throws the expected exception"""

        self.assertRaises(Unauthorized, _create_client,
                          user=_test_credentials['user'] + 'x',
                          password=_test_credentials['password'],
                          tenant=_test_credentials['tenant'],
                          auth_url=_test_credentials['auth_url'],
                          service_type=_test_credentials['service_type'])

        self.assertRaises(Unauthorized, _create_client,
                          user=_test_credentials['user'],
                          password=_test_credentials['password'] + 'x',
                          tenant=_test_credentials['tenant'],
                          auth_url=_test_credentials['auth_url'],
                          service_type=_test_credentials['service_type'])

        self.assertRaises(Unauthorized, _create_client,
                          user=_test_credentials['user'],
                          password=_test_credentials['password'],
                          tenant=_test_credentials['tenant'] + 'x',
                          auth_url=_test_credentials['auth_url'],
                          service_type=_test_credentials['service_type'])

        self.assertRaises(Unauthorized, _create_client,
                          user=_test_credentials['user'],
                          password=_test_credentials['password'],
                          tenant=_test_credentials['tenant'],
                          auth_url=_test_credentials['auth_url'] + 'x',
                          service_type=_test_credentials['service_type'])

        self.assertRaises(EndpointNotFound, _create_client,
                          user=_test_credentials['user'],
                          password=_test_credentials['password'],
                          tenant=_test_credentials['tenant'],
                          auth_url=_test_credentials['auth_url'],
                          service_type=_test_credentials['service_type'] + 'x')


# class VNFDSimpleTest(unittest.TestCase):
#     """
#     Test that a good onboard & destroy works as expected (simple) sinc
#     these VNFDs will be used in other VNFD and VNF tests
#     """
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFDOnboardTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFDDestroyTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFDListTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFDGetTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class SimpleVNFTest(unittest.TestCase):
#     """
#     Test that running a known good VNF works.  Used in setup for further VNF tests
#     """
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFListTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFGetTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFUpdateTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')
#
#
# class VNFDestroyTest(unittest.TestCase):
#     def setUp(self):
#         self.client = _create_client()
#         self.assertTrue(self.client is not None)
#
#     def tearDown(self):
#         self.client = None
#
#     @debug_on()
#     def testSomething(self):
#         """Verify something"""
#         self.fail('TODO: Implement some tests')


if __name__ == '__main__':

    # Last chance (under a debugger) to modify the unit test values before running the tests
    # Just you debugger conditions/commands to change _test_credentials['whatever']
    # Run the tests

    unittest.main()
