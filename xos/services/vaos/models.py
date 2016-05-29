# models.py -  vAOS Service Models

from core.models import Service, TenantWithContainer
from django.db import models, transaction

SERVICE_NAME = 'vaos'
SERVICE_NAME_VERBOSE = 'vAOS Service'
SERVICE_NAME_VERBOSE_PLURAL = 'vAOS Services'
TENANT_NAME_VERBOSE = 'vAOS Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'vAOS Tenants'


class VaosService(Service):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE

    service_message = models.CharField(max_length=254, help_text="Service Message to Display")


class VaosTenant(TenantWithContainer):

    KIND = SERVICE_NAME

    class Meta:
        verbose_name = TENANT_NAME_VERBOSE

    tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")

    def __init__(self, *args, **kwargs):
        vaosservice = VaosService.get_service_objects().all()
        if vaosservice:
            self._meta.get_field('provider_service').default = vaosservice[0].id
        super(VaosTenant, self).__init__(*args, **kwargs)

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

