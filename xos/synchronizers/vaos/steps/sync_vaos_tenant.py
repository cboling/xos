import os
import sys
from django.db.models import Q, F
from services.vaos.models import VaosService, VaosTenant
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVaosTenant(SyncInstanceUsingAnsible):

    provides = [VaosTenant]
    observes = VaosTenant
    requested_interval = 0
    template_name = "vaos_tenant_playbook.yaml"
    service_key_name = "/opt/xos/synchronizers/vaos/vaos_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVaosTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if (not deleted):
            objs = VaosTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:
            # If this is a deletion we get all of the deleted tenants..
            objs = VaosTenant.get_deleted_tenant_objects()

        return objs

    def get_vaos_service(self, o):
        if not o.provider_service:
            return None

        service = VaosService.get_service_objects().filter(id=o.provider_service.id)

        if not service:
            return None

        return service[0]

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        service = self.get_vaos_service(o)
        fields['service_message'] = service.service_message
        return fields

