#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.tests.test_api
    :synopsis: api unit test module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""

import urllib
from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from . test_util import ResourceTestCaseMixin, HttpTestcaseMixin, Timer
from . import factories
from analytics_api.models import PageVisit
from analytics_api import serializers


class BaseApiTestCase(ResourceTestCaseMixin, HttpTestcaseMixin, APITestCase):
    def setUp(self):
        APITestCase.setUp(self)
        HttpTestcaseMixin.setUp(self)
        ResourceTestCaseMixin.setUp(self)
        self.extra_header = dict(self.user_agent_header())

    def tearDown(self):
        APITestCase.tearDown(self)
        HttpTestcaseMixin.setUp(self)
        ResourceTestCaseMixin.tearDown(self)

    def get_url_name(self):
        return self.url_name

    def make_post_url(self, url):
        encoded = urllib.urlencode({'apikey': self.api_key})
        authorized = '{}?{}'.format(url, encoded)
        return authorized

    def api_key_get_params(self, api_key=None):
        apikey = api_key or self.api_key
        return dict(apikey=apikey)

    def limit_get_params(self, limit=None):
        limit = limit or self.limit
        return dict(limit=limit)

    def get_params(self, **kwargs):
        fns = self.api_key_get_params, self.limit_get_params
        params = dict()
        for fn in fns:
            params.update(fn(**kwargs))
        return params


class ApiRootTestCase(BaseApiTestCase):
    url_name = 'api_root'
    url = reverse(url_name)

    def get_extra_header(self):
        extra_header = self.extra_header
        extra_header.update(self.get_credentials())
        return extra_header

    def test_api_root_authenticated(self):

        with  Timer(self.get_url_name(), verbose=True):
            response = self.client.get(self.url,
                format='json',
                data=self.get_params(),
                **self.get_extra_header())

        self.assertHttpOK(response)
        self.validate_response(response)

    def test_api_root_not_authenticated(self):

        response = self.client.get(self.url,
            format='json',
            data=self.get_params(),
             **self.extra_header)

        self.assertHttpUnauthorized(response)

    def validate_response(self, response, **kwargs):

        contents = self.deserialize(response)
        self.assertEqual(len(contents), 4)
        expected = 'http://testserver/api/{}/'
        for key in ('domains', 'users', 'visits', 'pagediffs'):
            self.assertEqual(contents[key], expected.format(key))


class PageVisitTestCase(BaseApiTestCase):

    url_name = 'visit_list'
    url = reverse(url_name)

    def default_post_data(self):
        return dict(domain='gizmodo.com',
                     path='http://gizmodo.com',
                     subject='Home Page')

    def test_page_visit_post_authenticated(self):

        extra_header = dict(self.user_agent_header())

        with  Timer(self.url_name, verbose=True):
            response = self.client.post(self.make_post_url(self.url),
                format='json',
                data=self.default_post_data(),
                **extra_header)

        self.assertHttpCreated(response)
        self.validate_response(response)

    def test_page_visit_post_not_authenticated(self):

        extra_header = dict(self.user_agent_header())

        response = self.client.get(self.url,
            format='json',
            data=self.default_post_data(),
            **extra_header)

        self.assertHttpUnauthorized(response)

    def validate_response(self, response, **kwargs):
        contents = self.deserialize(response)
        self.assertEqual(len(contents), 1)
        url = str(contents['url'])
        pk = url.rsplit('/', 2)[1]
        self.assertTrue(PageVisit.objects.get(pk=pk))


class BasePageDiffTestCase(BaseApiTestCase):

    url_name = 'page_diffs'
    url = reverse(url_name)

    def get_params(self, direction=None, from_time=None, to_time=None):
        direction = direction or 'increasing'
        if from_time is None and to_time is None:
            from_time = timezone.now().strftime('%Y-%m-%d %H:%M')
            to_time = from_time
        if from_time is None:
            pass
        if to_time is None:
            pass
        params = dict(domain='gizmodo.com',
                      direction=serializers.DELTA_UP,
                      from_time=from_time,
                      to_time=to_time)
        params.update(super(BasePageDiffTestCase, self).get_params())
        return params

    def validate_response(self, response, **kwargs):
        expected = kwargs.get('expected')
        contents = self.deserialize(response)
        self.assertEqual(contents, expected)


class NoDataPageDiffTestCase(BasePageDiffTestCase):
    """
    Not stats data in db
    """
    expected = {'count': 0, 'previous': None,
                    'results': [], 'next': None}

    def test_page_diff_no_data_authenticated(self):

        with  Timer(self.url_name, verbose=True):
            response = self.client.get(self.make_post_url(self.url),
                format='json',
                data=self.get_params(),
                **self.extra_header)

        self.assertHttpOK(response)
        self.validate_response(response, expected=self.expected)


class SinglePageStatsTestCase(BasePageDiffTestCase):
    """
    Only a single stats object in db
    """
    expected = {'count': 0, 'previous': None,
                    'results': [], 'next': None}

    def setUp(self):
        super(SinglePageStatsTestCase, self).setUp()
        self.page_stats = factories.PageStatisticsFactory.create_stats(
                    stats_count=1, interval=5,
                    page_count=1,
                    domain_name='gizmodo.com')

    def test_page_diff_single_object_authenticated(self):
        with  Timer(self.url_name, verbose=True):
            response = self.client.get(self.make_post_url(self.url),
                format='json',
                data=self.get_params(),
                **self.extra_header)

        self.assertHttpOK(response)
        self.validate_response(response, expected=self.expected)


class PageDiffTestCase(BasePageDiffTestCase):
    """
    Two stats objects in db
    """

    expected = {
        'count': 1,
        'previous': None,
        'next': None,
        'results': [
            {
             'path': 'http://path_root/path_child/1',
             'change': 2,
             'subject': 'Subject_1'
            }
        ]
    }

    def setUp(self):
        super(PageDiffTestCase, self).setUp()
        self.page_stats = factories.PageStatisticsFactory.create_stats(
                    stats_count=2, interval=5,
                    page_count=1,
                    domain_name='gizmodo.com')

    def test_page_diff_authenticated(self):
        with  Timer(self.url_name, verbose=True):
            response = self.client.get(self.make_post_url(self.url),
                format='json',
                data=self.get_params(),
                **self.extra_header)

        self.assertHttpOK(response)
        self.validate_response(response, expected=self.expected)
