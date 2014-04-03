#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.admin
    :synopsis: analytics_api Django admin integration  module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
from django.contrib import admin
from django import forms

from analytics_api.models import Domain, PageStatistics, PageVisit, Page


class BaseAppModelAdminForm(forms.ModelForm):
    """
    Base model Django admin model form class
    """
    class Meta:
        localized_fields = ('creation_time',)

    def __init__(self, *args, **kwargs):
        super(BaseAppModelAdminForm, self).__init__(*args, **kwargs)
        assert True


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base Django model admin  class
    """
    form = BaseAppModelAdminForm
    list_display = ('id', 'creation_time', 'creation_user')
    list_filter = ('creation_time',)
    date_hierarchy = 'creation_time'
    exclude = tuple()
    readonly_fields = ('id', 'creation_time')
    ordering = ('creation_time',)


class DomainAdmin(admin.ModelAdmin):
    """
    Domain Django model admin  class
    """
    list_display = BaseModelAdmin.list_display + ('name',)


class PageAdmin(admin.ModelAdmin):
    """
    Page Django model admin  class
    """
    list_display = (BaseModelAdmin.list_display
        + ('path', 'visitors', 'subject'))


class PageVisitAdmin(admin.ModelAdmin):
    """
    Page visit Django  model admin  class
    """
    list_display = (BaseModelAdmin.list_display
        + ('domain', 'path', 'subject', 'api_key', 'ip_address', 'user_agent'))

_models = (Domain, PageStatistics, PageVisit, Page)
_admins = (DomainAdmin, BaseModelAdmin, PageVisitAdmin, PageAdmin)
for _model, _admin  in zip(_models, _admins):
    admin.site.register(_model, _admin)
