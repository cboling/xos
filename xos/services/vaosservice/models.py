# models.py -  vAOS Service Models

from core.models import Service, Tenant, User
from django.db import models, transaction
from xos.exceptions import *

SERVICE_NAME = 'vaosservice'
SERVICE_NAME_VERBOSE = 'vAOS Service'
SERVICE_NAME_VERBOSE_PLURAL = 'vAOS Services'
TENANT_NAME_VERBOSE = 'vAOS Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'vAOS Tenants'

SERVICE_VNFD_TEMPLATE = "/opt/xos/services/vaosservice/vaos_vnfd_template.yaml"
TENANT_PARAMETER_TEMPLATE = "/opt/xos/synchronizers/vaosservice/steps/vaos_tenant.yaml"


class VaosService(Service):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE

    def __init__(self, *args, **kwargs):
        self.vnfd_template = SERVICE_VNFD_TEMPLATE
        self.vnf_parameter_template = TENANT_PARAMETER_TEMPLATE
        super(VaosService, self).__init__(*args, **kwargs)

    @property
    def vnfd_template_file(self):
        return self.vnfd_template

    @property
    def vnf_parameter_template_file(self):
        return self.vnf_parameter_template


class VaosTenant(Tenant):

    KIND = SERVICE_NAME

    class Meta:
        verbose_name = TENANT_NAME_VERBOSE
        proxy = True

    default_attributes = {
        "s_tag": -1,
        "c_tag": None,
        "compute_node_name": None,
        "instance_id": None,
        "instance_name": None,
    }

    def __init__(self, *args, **kwargs):
        self.cached_creator = None
        vaosservice = VaosService.get_service_objects().all()

        if vaosservice:
            self._meta.get_field('provider_service').default = vaosservice[0].id
        super(VaosTenant, self).__init__(*args, **kwargs)

    @property
    def s_tag(self):
        return self.get_attribute("s_tag", self.default_attributes["s_tag"])

    @s_tag.setter
    def s_tag(self, value):
        self.set_attribute("s_tag", value)

    @property
    def c_tag(self):
        return self.get_attribute("c_tag", self.default_attributes["c_tag"])

    @c_tag.setter
    def c_tag(self, value):
        self.set_attribute("c_tag", value)

    @property
    def compute_node_name(self):
        return self.get_attribute("compute_node_name", self.default_attributes["compute_node_name"])

    @compute_node_name.setter
    def compute_node_name(self, value):
        self.set_attribute("compute_node_name", value)

    @property
    def instance_id(self):
        return self.get_attribute("instance_id", self.default_attributes["instance_id"])

    @instance_id.setter
    def instance_id(self, value):
        self.set_attribute("instance_id", value)

    @property
    def instance_name(self):
        return self.get_attribute("instance_name", self.default_attributes["instance_name"])

    @instance_name.setter
    def instance_name(self, value):
        self.set_attribute("instance_name", value)

    @property
    def creator(self):
        if getattr(self, "cached_creator", None):
            return self.cached_creator
        creator_id = self.get_attribute("creator_id")
        if not creator_id:
            return None
        users = User.objects.filter(id=creator_id)
        if not users:
            return None
        user = users[0]
        self.cached_creator = users[0]
        return user

    @creator.setter
    def creator(self, value):
        if value:
            value = value.id
        if value != self.get_attribute("creator_id", None):
            self.cached_creator = None

        self.set_attribute("creator_id", value)

    def save(self, *args, **kwargs):
        super(VaosTenant, self).save(*args, **kwargs)
        model_policy_vaos_tenant(self.pk)

    def delete(self, *args, **kwargs):
        # self.cleanup_container()
        super(VaosTenant, self).delete(*args, **kwargs)


def model_policy_vaos_tenant(pk):
    with transaction.atomic():
        tenant = VaosTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        # tenant = tenant[0]
        # tenant.manage_container()

