

class ControllerTest:
    def __init__(self, user, password, tenant, auth_url):
        self.admin_user = user
        self.admin_password = password
        self.admin_tenant = tenant
        self.auth_url = auth_url


class SiteTest:
    def __init__(self, user, password, tenant, auth_url):
        self.controller = ControllerTest(user, password, tenant, auth_url)

