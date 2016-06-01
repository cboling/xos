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
from plus import PlusSerializerMixin

from services.vaosservice.models import VaosTenant, VaosService


def get_default_vaos_service():
    services = VaosService.get_service_objects().all()
    if services:
        return services[0]
    return None


class VaosTenantForAPI(VaosTenant):
    class Meta:
        proxy = True
        app_label = "cord"

    # TODO: Support API in future
    # @property
    # def subscriber(self):
    #     return self.subscriber_root.id
    #
    # @subscriber.setter
    # def subscriber(self, value):
    #     self.subscriber_root = value # CordSubscriberRoot.get_tenant_objects().get(id=value)
    #
    # @property
    # def related(self):
    #     related = {}
    #     if self.vcpe:
    #         related["vsg_id"] = self.vcpe.id
    #         if self.vcpe.instance:
    #             related["instance_id"] = self.vcpe.instance.id
    #             related["instance_name"] = self.vcpe.instance.name
    #             related["wan_container_ip"] = self.vcpe.wan_container_ip
    #             if self.vcpe.instance.node:
    #                 related["compute_node_name"] = self.vcpe.instance.node.name
    #     return related


class VaosTenantSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VaosService.get_service_objects().all(),
                                                              default=get_default_vaos_service)
        s_tag = serializers.CharField()
        c_tag = serializers.CharField()
        backend_status = ReadOnlyField()
        # TODO Add later -> computeNodeName = serializers.SerializerMethodField("getComputeNodeName")

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = VaosTenantForAPI
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_id', 's_tag', 'c_tag',
                      'backend_status')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()


class VaosTenantViewSet(XOSViewSet):
    base_name = "vaostenant"
    method_name = "vaostenant"
    method_kind = "viewset"
    queryset = VaosTenantForAPI.get_tenant_objects().all()
    serializer_class = VaosTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(VaosTenantViewSet, self).get_urlpatterns(api_path=api_path)

        # example to demonstrate adding a custom endpoint
        # patterns.append(self.detail_url("s_tag/$", {"get": "get_s_tag", "put": "set_s_tag"}, "s_tag"))

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        c_tag = self.request.query_params.get('c_tag', None)
        if c_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("c_tag", None)==c_tag]
            queryset = queryset.filter(id__in=ids)

        s_tag = self.request.query_params.get('s_tag', None)
        if s_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("s_tag", None)==s_tag]
            queryset = queryset.filter(id__in=ids)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)