#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.serializers
    :synopsis: Model class serializers


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""

from django.contrib.auth.models import User
from rest_framework import serializers
from analytics_api.models import Domain, PageVisit
from analytics_api import fields

RESPONSE_LIMIT_MAX = 100
RESPONSE_LIMIT_MIN = 50
IP_ADDRESS_MAX_LEN = 128
DELTA_UP = 'up'
DELTA_DOWN = 'down'
DELTA_UPDOWN = 'both'
DELTAS = (DELTA_UP,
                     DELTA_DOWN, DELTA_UPDOWN)

# @ TODO: replace with custom request helper methods


def ip_address(request):
    return request.META['REMOTE_ADDR']


def user_agent(request):
    try:
        return request.META['USER_AGENT']
    except KeyError:
        return request.META['HTTP_USER_AGENT']


def apikey(request):
    return request.QUERY_PARAMS['apikey']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    User model serializer class
    """
    class Meta:
        model = User
        fields = ('username',)


class AppBaseModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Application abstract base serializer class
    """
    class Meta:
        fields = ('id', 'creation_time', )


class DomainSerializer(AppBaseModelSerializer):
    """
    Doman model serializer class
    """
    class Meta(AppBaseModelSerializer.Meta):
        model = Domain
        fields = AppBaseModelSerializer.Meta.fields + ('name',)


class PageVisitSerializer(AppBaseModelSerializer):
    """
    Page visit  model serializer class
    """
    class Meta(AppBaseModelSerializer.Meta):
        model = PageVisit
        fields = (AppBaseModelSerializer.Meta.fields
                 + ('domain', 'path', 'subject',
                    'api_key', 'ip_address', 'user_agent'))


uuid32_regex = ('[a-f0-9]{8}'
                 '-?[a-f0-9]{4}'
                 '-?4[a-f0-9]{3}'
                 '-?[89ab][a-f0-9]{3}'
                 '-?[a-f0-9]{12}')

apikey_regex = '[a-fA-F0-9]{40}'


class BaseResponseSerializer(serializers.Serializer):
    pass


class PageDiffResponseSerializer(BaseResponseSerializer):
    """
    Page diff response serializer class
    """
    class Meta(object):
        pass

    path = serializers.URLField()
    subject = serializers.CharField()
    change = serializers.IntegerField()


class BaseRequestSerializer(serializers.Serializer):
    class Meta(object):
        fields = ('apikey', 'limit', 'ip_address', 'user_agent')

    apikey = serializers.RegexField(apikey_regex,
         min_length=fields.API_KEY_FIELD_MAX_LENGTH,
         max_length=fields.API_KEY_FIELD_MAX_LENGTH,
                                     required=True)

    limit = serializers.IntegerField(min_value=0,
                                     max_value=RESPONSE_LIMIT_MAX,
                                     required=False,
                                     default=RESPONSE_LIMIT_MIN)

    user_agent = serializers.CharField(
            max_length=fields.USER_AGENT_FIELD_MAX_LENGTH,
            required=True)

    ip_address = serializers.CharField(
            max_length=IP_ADDRESS_MAX_LEN,
            required=True)

    def __init__(self, request):
        super(BaseRequestSerializer, self).__init__(
                data=self.get_data(request, self.Meta.fields))

    def get_data(self, request, fields):
        data = {}
        for field in fields:
            fn = getattr(self, 'raw_' + field)
            value = fn(request)
            if value is not None:
                data[field] = value
        return data

    def cleaned_ip_address(self):
        return self.data['ip_address']

    def raw_ip_address(self, request):
        return ip_address(request)

    def cleaned_user_agent(self):
        return self.data['user_agent']

    def raw_user_agent(self, request):
        return user_agent(request)

    def cleaned_apikey(self):
        return self.data['apikey']

    def raw_apikey(self, request):
        return apikey(request)

    def cleaned_domain(self):
        return self.data.get('domain')

    def raw_domain(self, request):
        return request.QUERY_PARAMS.get('domain', None)

    def cleaned_limit(self):
        return self.data.get('limit')

    def raw_limit(self, request):
        return request.QUERY_PARAMS.get('limit')

    def cleaned_name(self):
        return self.data.get('name')

    def raw_name(self, request):
        return request.QUERY_PARAMS.get('name', None)


class DomainRequestSerializer(BaseRequestSerializer):
    """
    Domain request serializer class
    """
    class Meta(object):
        fields = (BaseRequestSerializer.Meta.fields
                  + ('name', ))

    name = serializers.CharField(
            max_length=fields.NAME_FIELD_MAX_LENGTH, required=False)


class PageDiffRequestSerializer(BaseRequestSerializer):
    """
    Page diff request serializer class
    """
    class Meta(object):
        fields = (BaseRequestSerializer.Meta.fields
                  + ('domain', 'from_time', 'to_time',
                     'direction'))

    domain = serializers.CharField(
            max_length=fields.NAME_FIELD_MAX_LENGTH, required=True)

    from_time = serializers.DateTimeField(required=False)
    to_time = serializers.DateTimeField(required=False)
    direction = serializers.ChoiceField(
        required=False,
        choices=zip(DELTAS, DELTAS),
        default=DELTA_UP)

    def cleaned_direction(self):
        return self.data.get('direction')

    def raw_direction(self, request):
        return request.QUERY_PARAMS.get('direction')

    def cleaned_from_time(self):
        return self.data.get('from_time')

    def raw_from_time(self, request):
        return request.QUERY_PARAMS.get('from_time')

    def cleaned_to_time(self):
        return self.data.get('to_time')

    def raw_to_time(self, request):
        return request.QUERY_PARAMS.get('to_time')
