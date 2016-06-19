#!/usr/bin/python

from defaults import *
from TackerTestClasses import SiteTest
import unittest
from xos.synchronizers.base import tacker
from tackerclient.client import HTTPClient, construct_http_client
from tackerclient.common.exceptions import Unauthorized, ConnectionFailed
from tackerclient.common.exceptions import SslCertificateValidationError
from requests.exceptions import HTTPError
import argparse

# These credentials from 'defaults.py' can be assigned on the command line via argparse
_test_credentials = {
    'user': OPENSTACK_USER,
    'password': OPENSTACK_PASSWORD,
    'tenant': OPENSTACK_TENANT_NAME,
    'auth_url': OPENSTACK_AUTH_URL,
    'service_type': OPENSTACK_SERVICE_TYPE
}


def _create_site(user=OPENSTACK_USER, password=OPENSTACK_PASSWORD,
                 tenant=OPENSTACK_TENANT_NAME, auth_url=OPENSTACK_AUTH_URL):
    return SiteTest(user=user,
                    password=password,
                    tenant=tenant,
                    auth_url=auth_url)


def _create_client(credentials=_test_credentials):
    return tacker.construct_http_client(user=credentials['user'],
                                        password=credentials['password'],
                                        tenant=credentials['tenant'],
                                        auth_url=credentials['auth_url'],
                                        service_type=credentials['service_type'])


def _onboard_vnfd(client, vnfd_file):
    """
    Onboard a known good VNFD
    :param client:
    :param vnfd_file:
    :return:
    """
    pass


class CredentialsTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()

    def tearDown(self):
        self.client = None

    def testClientLogin(self):
        """Verify our credentials are valid"""
        self.assertTrue(self.client is not None)
        self.assertIsInstance(self.client, HTTPClient)

    def testInvalidClientLoginUser(self):
        """Verify bad credentials are not valid and throws exception"""

        self.assertRaises(Unauthorized, _create_client,
                          user=OPENSTACK_USER + 'x',
                          password=OPENSTACK_PASSWORD,
                          tenant=OPENSTACK_TENANT_NAME,
                          auth_url=OPENSTACK_AUTH_URL,
                          service_type=OPENSTACK_SERVICE_TYPE)

        self.assertRaises(Unauthorized, _create_client,
                          user=OPENSTACK_USER,
                          password=OPENSTACK_PASSWORD + 'x',
                          tenant=OPENSTACK_TENANT_NAME,
                          auth_url=OPENSTACK_AUTH_URL,
                          service_type=OPENSTACK_SERVICE_TYPE)

        self.assertRaises(Unauthorized, _create_client,
                          user=OPENSTACK_USER,
                          password=OPENSTACK_PASSWORD,
                          tenant=OPENSTACK_TENANT_NAME + 'x',
                          auth_url=OPENSTACK_AUTH_URL,
                          service_type=OPENSTACK_SERVICE_TYPE)

        self.assertRaises(Unauthorized, _create_client,
                          user=OPENSTACK_USER,
                          password=OPENSTACK_PASSWORD,
                          tenant=OPENSTACK_TENANT_NAME,
                          auth_url=OPENSTACK_AUTH_URL + 'x',
                          service_type=OPENSTACK_SERVICE_TYPE)

        self.assertRaises(Unauthorized, _create_client,
                          user=OPENSTACK_USER,
                          password=OPENSTACK_PASSWORD,
                          tenant=OPENSTACK_TENANT_NAME,
                          auth_url=OPENSTACK_AUTH_URL,
                          service_type=OPENSTACK_SERVICE_TYPE + 'x')


class VNFDSimpleTest(unittest.TestCase):
    """
    Test that a good onboard & destroy works as expected (simple) sinc
    these VNFDs will be used in other VNFD and VNF tests
    """
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDOnboardTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDDestroyTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDListTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDGetTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class SimpleVNFTest(unittest.TestCase):
    """
    Test that running a known good VNF works.  Used in setup for further VNF tests
    """
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFListTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFGetTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFUpdateTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDestroyTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tacker Unit Test')

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

    _test_credentials = {
        'user': args.username,
        'password': args.password,
        'tenant': args.tenant,
        'auth_url': args.auth_url,
        'service_type': args.service_type
    }
    # Run the tests

    unittest.main()
