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

from services.vaosservice.models import VaosTenant, VaosService

def get_default_vaos_service():
    services = VaosService.get_service_objects().all()
    if services:
        return services[0]
    return None


class VaosTenantSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VaosService.get_service_objects().all(),
                                                              default=get_default_vaos_service)
        s_tag = serializers.CharField()
        c_tag = serializers.CharField()

        backend_status = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = VaosTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_id', 's_tag', 'c_tag', 'backend_status')

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
        # patterns.append(self.detail_url("s_tag/$", {"get": "get_s_tag", "put": "set_s_tag"}, "s_tag"))

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_s_tag(self, request, pk=None):
        tenant = self.get_object()
        return Response({"s_tag": tenant.s_tag})

    def set_s_tag(self, request, pk=None):
        tenant = self.get_object()
        tenant.s_tag = request.data["s_tag"]
        tenant.save()
        return Response({"s_tag": tenant.s_tag})

    def get_c_tag(self, request, pk=None):
        tenant = self.get_object()
        return Response({"c_tag": tenant.c_tag})

    def set_c_tag(self, request, pk=None):
        tenant = self.get_object()
        tenant.c_tag = request.data["c_tag"]
        tenant.save()
        return Response({"c_tag": tenant.c_tag})


class VaosTenantList(XOSListCreateAPIView):
    # TODO Need to wire this in
    serializer_class = VaosTenantSerializer

    method_kind = "list"
    method_name = "vaostenant"

    def get_queryset(self):
        queryset = VaosTenant.get_tenant_objects().select_related().all()

        service_specific_id = self.request.query_params.get('service_specific_id', None)
        if service_specific_id is not None:
            queryset = queryset.filter(service_specific_id=service_specific_id)

        #        vlan_id = self.request.query_params.get('vlan_id', None)
        #        if vlan_id is not None:
        #            ids = [x.id for x in queryset if x.get_attribute("vlan_id", None)==vlan_id]
        #            queryset = queryset.filter(id__in=ids)

        c_tag = self.request.query_params.get('c_tag', None)
        if c_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("c_tag", None)==c_tag]
            queryset = queryset.filter(id__in=ids)

        s_tag = self.request.query_params.get('s_tag', None)
        if s_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("s_tag", None)==s_tag]
            queryset = queryset.filter(id__in=ids)

        return queryset

    def post(self, request, format=None):
        data = request.DATA

        existing_obj = None
        for obj in VaosTenant.get_tenant_objects().all():
            if (obj.c_tag == data.get("c_tag", None)) and (obj.s_tag == data.get("s_tag", None)) and  (obj.service_specific_id == data.get("service_specific_id",None)):
                existing_obj = obj

        if existing_obj:
            serializer = VaosTenantSerializer(existing_obj)
            headers = self.get_success_headers(serializer.data)
            return Response( serializer.data, status=status.HTTP_200_OK )

        return super(VaosTenantList, self).post(request, format)


class VaosTenantDetail(XOSRetrieveUpdateDestroyAPIView):
    # TODO Need to wire this in
    serializer_class = VaosTenantSerializer
    queryset = VaosTenant.get_tenant_objects().select_related().all()

    method_kind = "detail"
    method_name = "vaostenant"
