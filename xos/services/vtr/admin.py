from django.contrib import admin

from services.cord.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline
from core.middleware import get_request

from services.vtr.models import *
from services.cord.models import CordSubscriberRoot

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class VTRServiceAdmin(ReadOnlyAwareAdmin):
    model = VTRService
    verbose_name = "vTR Service"
    verbose_name_plural = "vTR Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'vTR Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('vtradmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VTRService.get_service_objects_by_user(request.user)

class VTRTenantForm(forms.ModelForm):
    simple_attributes = {"test": None,
                         "argument": None,
                         "result": None,
                         "target": None}
    test = forms.ChoiceField(choices=VTRTenant.TEST_CHOICES, required=True)
    argument = forms.CharField(required=False)
    result = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 10, 'cols': 80, 'class': 'input-xxlarge'}))
    target = forms.ModelChoiceField(queryset=CordSubscriberRoot.objects.all())

    def __init__(self,*args,**kwargs):
        super (VTRTenantForm,self ).__init__(*args,**kwargs)
        self.fields['provider_service'].queryset = VTRService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['test'].initial = self.instance.test
            self.fields['argument'].initial = self.instance.argument
            self.fields['target'].initial = self.instance.target
            self.fields['result'].initial = self.instance.result
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = VTR_KIND
            if VTRService.get_service_objects().exists():
               self.fields["provider_service"].initial = VTRService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.test = self.cleaned_data.get("test")
        self.instance.argument = self.cleaned_data.get("argument")
        self.instance.target = self.cleaned_data.get("target")
        self.instance.result = self.cleaned_data.get("result")
        return super(VTRTenantForm, self).save(commit=commit)

    class Meta:
        model = VTRTenant

class VTRTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'target', 'test', 'argument' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', # 'subscriber_root', 'service_specific_id', 'service_specific_attribute',
                                     'target', 'test', 'argument', 'result'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute')
    form = VTRTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VTRTenant.get_tenant_objects_by_user(request.user)

admin.site.register(VTRService, VTRServiceAdmin)
admin.site.register(VTRTenant, VTRTenantAdmin)

