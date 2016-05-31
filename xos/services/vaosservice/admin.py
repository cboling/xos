# admin.py - vAOS Service Django Admin

from core.admin import ReadOnlyAwareAdmin, SliceInline
from core.middleware import get_request
from core.models import User

from django import forms
from django.contrib import admin

from services.vaosservice.models import *


class VaosServiceForm(forms.ModelForm):

    class Meta:
        model = VaosService

    def __init__(self, *args, **kwargs):
        super(VaosServiceForm, self).__init__(*args, **kwargs)

        # if self.instance:
        #    self.fields['service_message'].initial = self.instance.service_message

    def save(self, commit=True):
        # self.instance.service_message = self.cleaned_data.get('service_message')
        return super(VaosServiceForm, self).save(commit=commit)


class VaosServiceAdmin(ReadOnlyAwareAdmin):

    model = VaosService
    verbose_name = SERVICE_NAME_VERBOSE
    verbose_name_plural = SERVICE_NAME_VERBOSE_PLURAL
    form = VaosServiceForm
    inlines = [SliceInline]

    # list_display = ('backend_status_icon', 'name', 'service_message', 'enabled')
    # list_display_links = ('backend_status_icon', 'name', 'service_message' )
    list_display = ('backend_status_icon', 'name', 'enabled')
    list_display_links = ('backend_status_icon', 'name')

    fieldsets = [(None, {
        # 'fields': ['backend_status_text', 'name', 'enabled', 'versionNumber', 'service_message', 'description',],
        'fields': ['backend_status_text', 'name', 'enabled', 'versionNumber', 'description'],
        'classes':['suit-tab suit-tab-general'],
        })]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['name', 'enabled', 'versionNumber', 'description']

    extracontext_registered_admins = True

    suit_form_tabs = (
        ('general', 'vAOS Service Details', ),
        ('administration', 'Administration'),
        ('slices', 'Slices',),
        )

    suit_form_includes = ((
        'top',
        'administration'),
        )

    def queryset(self, request):
        return VaosService.get_service_objects_by_user(request.user)

admin.site.register(VaosService, VaosServiceAdmin)


class VaosTenantForm(forms.ModelForm):

    class Meta:
        model = VaosTenant

    s_tag = forms.CharField()
    c_tag = forms.CharField()
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        super(VaosTenantForm, self).__init__(*args, **kwargs)

        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['kind'].initial = SERVICE_NAME
        self.fields['provider_service'].queryset = VaosService.get_service_objects().all()

        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields['c_tag'].initial = self.instance.c_tag
            self.fields['s_tag'].initial = self.instance.s_tag

        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            if VaosService.get_service_objects().exists():
                self.fields['provider_service'].initial = VaosService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.s_tag = self.cleaned_data.get("s_tag")
        self.instance.c_tag = self.cleaned_data.get("c_tag")
        self.instance.creator = self.cleaned_data.get('creator')
        return super(VaosTenantForm, self).save(commit=commit)


class VaosTenantAdmin(ReadOnlyAwareAdmin):

    verbose_name = TENANT_NAME_VERBOSE
    verbose_name_plural = TENANT_NAME_VERBOSE_PLURAL

    list_display = ('id', 'backend_status_icon', 'instance', 'id', 'service_specific_id', 's_tag', 'c_tag')
    list_display_links = ('backend_status_icon', 'instance', 'id')

    fieldsets = [(None, {
        'fields': ['backend_status_text', 'kind', 'provider_service', 'instance', 'creator', 'service_specific_id', 's_tag', 'c_tag'],
        'classes': ['suit-tab suit-tab-general'],
        })]

    readonly_fields = ('backend_status_text', 'instance',)

    form = VaosTenantForm

    suit_form_tabs = (('general', 'Details'),)

    def queryset(self, request):
        return VaosTenant.get_tenant_objects_by_user(request.user)

admin.site.register(VaosTenant, VaosTenantAdmin)

