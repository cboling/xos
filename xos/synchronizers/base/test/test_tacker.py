#!/usr/bin/python

import unittest
from defaults import *
from TackerTestClasses import SiteTest
from synchronizers.base import tacker
from tackerclient.client import HTTPClient, construct_http_client
from tackerclient.common.exceptions import Unauthorized, ConnectionFailed
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

    'auth_url': 'http://10.0.3.41:35357/v2.0',      # Some various configs for testing, this one is lxc
    # 'auth_url': OPENSTACK_AUTH_URL,
}


def _create_site(user=OPENSTACK_USER, password=OPENSTACK_PASSWORD,
                 tenant=OPENSTACK_TENANT_NAME, auth_url=OPENSTACK_AUTH_URL):
    return SiteTest(user=user,
                    password=password,
                    tenant=tenant,
                    auth_url=auth_url)


def _create_client(credentials=_test_credentials):
    return tacker.get_tacker_client(_create_site(user=credentials['user'],
                                                 password=credentials['password'],
                                                 tenant=credentials['tenant'],
                                                 auth_url=credentials['auth_url']),
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

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDOnboardTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDDestroyTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDListTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
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

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFListTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFGetTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFUpdateTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


class VNFDestroyTest(unittest.TestCase):
    def setUp(self):
        self.client = _create_client()
        self.assertTrue(self.client is not None)

    def tearDown(self):
        self.client = None

    @debug_on()
    def testSomething(self):
        """Verify something"""
        self.fail('TODO: Implement some tests')


if __name__ == '__main__':

    # Last chance (under a debugger) to modify the unit test values before running the tests
    # Just you debugger conditions/commands to change _test_credentials['whatever']
    # Run the tests

    unittest.main()
