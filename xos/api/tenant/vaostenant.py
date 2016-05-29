from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.cord.models import CordSubscriberRoot
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

from services.vaos.models import VaosTenant, VaosService

def get_default_vaos_service():
    services = VaosService.get_service_objects().all()
    if services:
        return services[0]
    return None

class VaosTenantSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VaosService.get_service_objects().all(), default=get_default_vaos_service)
        tenant_message = serializers.CharField(required=False)
        backend_status = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = VaosTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'tenant_message', 'backend_status')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

class VaosTenantViewSet(XOSViewSet):
    base_name = "vaostenant"
    method_name = "vaostenant"
    method_kind = "viewset"
    queryset = VaosTenant.get_tenant_objects().all()
    serializer_class = VaosTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(VaosTenantViewSet, self).get_urlpatterns(api_path=api_path)

        # example to demonstrate adding a custom endpoint
        patterns.append( self.detail_url("message/$", {"get": "get_message", "put": "set_message"}, "message") )

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_message(self, request, pk=None):
        tenant = self.get_object()
        return Response({"tenant_message": tenant.tenant_message})

    def set_message(self, request, pk=None):
        tenant = self.get_object()
        tenant.tenant_message = request.data["tenant_message"]
        tenant.save()
        return Response({"tenant_message": tenant.tenant_message})

