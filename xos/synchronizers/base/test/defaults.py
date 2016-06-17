# Some basic defaults for the tests

# Credentials

OPENSTACK_USER = 'admin'
OPENSTACK_PASSWORD = 'devstack'
OPENSTACK_TENANT_NAME = 'admin'
OPENSTACK_AUTH_URL = 'http://localhost:35357/v2.0'
OPENSTACK_SERVICE_TYPE = 'nfv-orchestration'

class ControllerTest:
    def __init__(self, user, password, tenant, auth_url):
        self.admin_user = user
        self.admin_password = password
        self.admin_tenant = tenant
        self.auth_url = auth_url


class SiteTest:
    def __init__(self, user, password, tenant, auth_url):
        self.controller = ControllerTest(user, password, tenant, auth_url)

# Files (Templates/parameters/...)

TACKER_VNFD_YAML = 'files/cirros-mitaka.yaml'               # No parameters
TACKER_VNFD_TEMPLATE = 'files/radius-mitaka-template.yaml'  # Takes parameters
TACKER_VNF_PARAMETERS = 'files/radius-param.yaml'           # VNF template
TACKER_VNF_CONFIG = 'files/radius-config.yaml'              # Config for VNF launch
TACKER_VNF_UPDATE = 'files/radius-update.yaml'              # VNF configuration update

