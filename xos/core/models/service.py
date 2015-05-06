from django.db import models
from core.models import PlCoreBase,SingletonModel,PlCoreBaseManager
from core.models.plcorebase import StrippedCharField
from xos.exceptions import *
import json

class Service(PlCoreBase):
    # when subclassing a service, redefine KIND to describe the new service
    KIND = "generic"

    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    enabled = models.BooleanField(default=True)
    kind = StrippedCharField(max_length=30, help_text="Kind of service", default=KIND)
    name = StrippedCharField(max_length=30, help_text="Service Name")
    versionNumber = StrippedCharField(max_length=30, help_text="Version of Service Definition")
    published = models.BooleanField(default=True)
    view_url = StrippedCharField(blank=True, null=True, max_length=1024)
    icon_url = StrippedCharField(blank=True, null=True, max_length=1024)
    public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key string")

    def __init__(self, *args, **kwargs):
        # for subclasses, set the default kind appropriately
        self._meta.get_field("kind").default = self.KIND
        super(Service, self).__init__(*args, **kwargs)

    @classmethod
    def get_service_objects(cls):
        return cls.objects.filter(kind = cls.KIND)

    def __unicode__(self): return u'%s' % (self.name)

class ServiceAttribute(PlCoreBase):
    name = models.SlugField(help_text="Attribute Name", max_length=128)
    value = StrippedCharField(help_text="Attribute Value", max_length=1024)
    service = models.ForeignKey(Service, related_name='serviceattributes', help_text="The Service this attribute is associated with")

class Tenant(PlCoreBase):
    """ A tenant is a relationship between two entities, a subscriber and a
        provider.

        The subscriber can be a User, a Service, or a Tenant.

        The provider is always a Service.
    """

    CONNECTIVITY_CHOICES = (('public', 'Public'), ('private', 'Private'), ('na', 'Not Applicable'))

    # when subclassing a service, redefine KIND to describe the new service
    KIND = "generic"

    kind = StrippedCharField(max_length=30, default=KIND)
    provider_service = models.ForeignKey(Service, related_name='tenants')
    subscriber_service = models.ForeignKey(Service, related_name='subscriptions', blank=True, null=True)      # can we drop this ?
    subscriber_tenant = models.ForeignKey("Tenant", related_name='subscriptions', blank=True, null=True)
    subscriber_user = models.ForeignKey("User", related_name='subscriptions', blank=True, null=True)
    service_specific_id = StrippedCharField(max_length=30)
    service_specific_attribute = models.TextField()
    connect_method = models.CharField(null=False, blank=False, max_length=30, choices=CONNECTIVITY_CHOICES, default="na")

    def __init__(self, *args, **kwargs):
        # for subclasses, set the default kind appropriately
        self._meta.get_field("kind").default = self.KIND
        super(Tenant, self).__init__(*args, **kwargs)

    def __unicode__(self):
        if not hasattr(self, "provider_service"):
           # When the REST API does a POST on a CordSubscriber object, for
           # some reason there is no provider_service field. All of the other
           # fields are there. Provider_service is even in the dir(). However,
           # trying to getattr() on it will fail.
           return "confused-tenant-object"

        if self.subscriber_service:
            return u'%s service %s on service %s' % (str(self.kind), str(self.subscriber_service.id), str(self.provider_service.id))
        elif self.subscriber_tenant:
            return u'%s tenant %s on service %s' % (str(self.kind), str(self.subscriber_tenant.id), str(self.provider_service.id))
        else:
            return u'%s on service %s' % (str(self.kind), str(self.provider_service.id))

    # helper for extracting things from a json-encoded service_specific_attribute
    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    def set_attribute(self, name, value):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        attributes[name]=value
        self.service_specific_attribute = json.dumps(attributes)

    @classmethod
    def get_tenant_objects(cls):
        return cls.objects.filter(kind = cls.KIND)

    @classmethod
    def get_deleted_tenant_objects(cls):
        return cls.deleted_objects.filter(kind = cls.KIND)

    # helper function to be used in subclasses that want to ensure service_specific_id is unique
    def validate_unique_service_specific_id(self):
        if self.pk is None:
            if self.service_specific_id is None:
                raise XOSMissingField("subscriber_specific_id is None, and it's a required field", fields={"service_specific_id": "cannot be none"})

            conflicts = self.get_tenant_objects().filter(service_specific_id=self.service_specific_id)
            if conflicts:
                raise XOSDuplicateKey("service_specific_id %s already exists" % self.service_specific_id, fields={"service_specific_id": "duplicate key"})

class CoarseTenant(Tenant):
    class Meta:
        proxy = True

    KIND = "coarse"

    def save(self, *args, **kwargs):
        if (not self.subscriber_service):
            raise XOSValidationError("subscriber_service cannot be null")
        if (self.subscriber_tenant or self.subscriber_user):
            raise XOSValidationError("subscriber_tenant and subscriber_user must be null")

        super(CoarseTenant,self).save()
