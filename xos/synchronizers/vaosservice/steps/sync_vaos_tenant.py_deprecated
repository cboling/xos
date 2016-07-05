import os
import sys
from django.db.models import Q, F
from services.vaosservice.models import VaosService, VaosTenant
from synchronizers.base.SyncInstanceUsingTacker import SyncInstanceUsingTacker

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)


class SyncVaosTenant(SyncInstanceUsingTacker):
    provides = [VaosTenant]
    observes = VaosTenant
    requested_interval = 0
    service_key_name = "/opt/xos/synchronizers/vaosservice/vaos_private_key"

    def __init__(self, *args, **kwargs):
        service = VaosService.get_service_objects().filter(id=o.provider_service.id)
        self.vnfd_template = service.vnfd_template_file
        self.vnf_parameter_template = service.vnf_parameter_template_file
        super(SyncVaosTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if not deleted:
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
        # This is a place to include extra attributes that aren't part of the
        # object itself. In the case of vCPE, we need to know:
        #   1) vlan_ids, for setting up networking in the vAOS VM

        fields = {'s_tag': o.s_tag,
                  'c_tag': o.c_tag,
                  }

        # TODO: Do we want to retrieve anything from the service?
        # service = self.get_vaos_service(o)
        # fields['service_message'] = service.service_message
        return fields

    # def sync_fields(self, o, fields):
    #     # the super causes the playbook to be run
    #
    #     super(SyncVaosTenant, self).sync_fields(o, fields)
    #
    # def run_playbook(self, o, fields):
    #     ansible_hash = hashlib.md5(repr(sorted(fields.items()))).hexdigest()
    #     quick_update = (o.last_ansible_hash == ansible_hash)
    #
    #     if ENABLE_QUICK_UPDATE and quick_update:
    #         logger.info("quick_update triggered; skipping ansible recipe",extra=o.tologdict())
    #     else:
    #         if o.instance.isolation in ["container", "container_vm"]:
    #             super(SyncVSGTenant, self).run_playbook(o, fields, "sync_vcpetenant_new.yaml")
    #         else:
    #             if CORD_USE_VTN:
    #                 super(SyncVSGTenant, self).run_playbook(o, fields, template_name="sync_vcpetenant_vtn.yaml")
    #             else:
    #                 super(SyncVSGTenant, self).run_playbook(o, fields)
    #
    #     o.last_ansible_hash = ansible_hash
    #
    # def delete_record(self, m):
    #     pass
