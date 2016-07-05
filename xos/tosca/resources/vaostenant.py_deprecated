import importlib
import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
from core.models import Tenant, Service
from services.vaosservice.models import VaosTenant, SERVICE_NAME as VAOSTENANT_KIND
from xosresource import XOSResource


class XOSVaosTenant(XOSResource):
    provides = "tosca.nodes.VaosTenant"
    xos_model = VaosTenant
    name_field = "service_specific_id"
    copyin_props = ["s_tag", "c_tag"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVaosTenant, self).get_xos_args()

        # VaosTenant must always have a provider_service
        provider_name = self.get_requirement("tosca.relationships.TenantOfService", throw_exception=True)
        if provider_name:
            args["provider_service"] = self.get_xos_object(Service, throw_exception=True, name=provider_name)

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        return VaosTenant.get_tenant_objects().filter(provider_service=args["provider_service"],
                                                      service_specific_id=args["service_specific_id"])
        return []

    def can_delete(self, obj):
        return super(XOSVaosTenant, self).can_delete(obj)

