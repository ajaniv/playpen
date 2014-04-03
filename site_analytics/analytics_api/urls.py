#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.urls
    :synopsis: analytics_api application url configuration


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""

from django.conf.urls import patterns, url, include

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = format_suffix_patterns(patterns('',
    url(r'^$', views.api_root, name='api_root'),
    url(r'^users/$',
        views.UserListView.as_view(),
        name='user_list'),
    url(r'^domains/$',
        views.DomainListView.as_view(),
        name='domain_list'),
    url(r'^visits/$',
        views.VisitListView.as_view(),
        name='visit_list'),
    url(r'^visits/(?P<pk>[0-9]+)/$',
        views.VisitDetailView.as_view(),
        name='visit_detail'),
    url(r'^pagediffs/$',
        views.PageDiffView.as_view(),
        name='page_diffs'),
))

# Login and logout views for the browsable API
urlpatterns += patterns('',
    url(r'^api-auth/',
        include('rest_framework.urls',
                namespace='rest_framework')),
    url(r'^api-token-auth/',
        'rest_framework.authtoken.views.obtain_auth_token')
)
