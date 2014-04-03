#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics.urls
    :synopsis: top level url configuration module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'analytics.views.home', name='home'),
    url(r'^api/', include('analytics_api.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
