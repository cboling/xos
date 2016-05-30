# models.py -  vAOS Service Models

from core.models import Service, TenantWithContainer
from django.db import models, transaction

VCPE_KIND = "vAOS"
SERVICE_NAME = 'vaosservice'
SERVICE_NAME_VERBOSE = 'vAOS Service'
SERVICE_NAME_VERBOSE_PLURAL = 'vAOS Services'
TENANT_NAME_VERBOSE = 'vAOS Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'vAOS Tenants'


class VaosService(Service):

    # KIND = SERVICE_NAME
    KIND = VCPE_KIND

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE

    service_message = models.CharField(max_length=254, help_text="Service Message to Display")


class VaosTenant(TenantWithContainer):

    KIND = SERVICE_NAME

    class Meta:
        verbose_name = TENANT_NAME_VERBOSE

    tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")

    # default_attributes = {"vlan_id": None, "s_tag": None, "c_tag": None}

    def __init__(self, *args, **kwargs):
        vaosservice = VaosService.get_service_objects().all()
        if vaosservice:
            self._meta.get_field('provider_service').default = vaosservice[0].id
        super(VaosTenant, self).__init__(*args, **kwargs)

    # @property
    # def s_tag(self):
    #     return self.get_attribute("s_tag", self.default_attributes["s_tag"])
    #
    # @s_tag.setter
    # def s_tag(self, value):
    #     self.set_attribute("s_tag", value)
    #
    # @property
    # def c_tag(self):
    #     return self.get_attribute("c_tag", self.default_attributes["c_tag"])
    #
    # @c_tag.setter
    # def c_tag(self, value):
    #     self.set_attribute("c_tag", value)
    #
    # # for now, vlan_id is a synonym for c_tag
    #
    # @property
    # def vlan_id(self):
    #     return self.c_tag
    #
    # @vlan_id.setter
    # def vlan_id(self, value):
    #     self.c_tag = value

    def save(self, *args, **kwargs):
        super(VaosTenant, self).save(*args, **kwargs)
        model_policy_vaos_tenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(VaosTenant, self).delete(*args, **kwargs)


def model_policy_vaos_tenant(pk):
    with transaction.atomic():
        tenant = VaosTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()

