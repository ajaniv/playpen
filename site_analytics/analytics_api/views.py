#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.views
    :synopsis: API end point module

API views for request handling
.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
import datetime
import logging

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import mixins
from rest_framework import generics
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from analytics_api.models import Domain, PageVisit, PageStatistics
from analytics_api import serializers

logger = logging.getLogger(__name__)
#
#
# Caution: class inheritance order requires extra care due
# to the high level of integration of mixin classes
# and the underlying MRO logic
#
#

DEFAULT_QUERY_LIMIT = 100


def get_authorization_header(request):
    """
    Return request's authorization data
    """
    auth = request.QUERY_PARAMS.get('apikey', None)

    return auth

get_api_key = get_authorization_header


class ParamAuthentication(authentication.BaseAuthentication):
    """
    Url parameter token based authentication.

    Required for non-header authorization token
    """

    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request)

        if not auth:
            return None

        return self.authenticate_credentials(auth)

    def authenticate_credentials(self, key):
        try:
            #@TODO: replace with in-process cache based lookup
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        return (token.user, token)

    def authenticate_header(self, request):
        return 'Token'


class AppCreateModelMixin(mixins.CreateModelMixin):
    """
    Object creation helper class
    """
    def pre_save(self, obj):
        """
        Hook for modifying object prior to saving
        @see base class implementation
        """
        #@TODO: push to a base class
        obj.creation_user = self.request.user


class AppView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    Base class for application API views
    """
    authentication_classes = (ParamAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Handle get request - debug hook
        @see base class implementation
        """
        serializer = self.request_serializer_class(request)
        if serializer.is_valid():
            request.serializer = serializer
            return self.list(request, *args, **kwargs)
        raise ValidationError(serializer.errors)

    def domain_filter(self, qs):
        """
        Filter by the domain
        """
        #@ todo: may need to support multiple domains
        domain = self.request.serializer.cleaned_domain
        if domain:
            qs = qs.filter(domain=domain)
        return qs

    def limit_filter(self, qs):
        """
        Filter the number of results returned
        """
        limit = self.request.serializer.cleaned_limit()
        if limit:
            qs = qs[0:int(limit)]
        return qs


class UserListView(AppView):
    """
    User listing end-point view class.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    #@TODO: extend to provide user, token info for authorized users


class DomainListView(AppView):
    """
    Domain listing end-point  view class.
    """
    queryset = Domain.objects.all()
    serializer_class = serializers.DomainSerializer
    request_serializer_class = serializers.DomainRequestSerializer

    def name_filter(self, qs):
        """
        Filter by the name
        """
        name = self.request.serializer.cleaned_name()
        if name:
            qs = qs.filter(name=name)
        return qs

    def get_queryset(self):
        """
        Filter the query based on request parameters
        @see base class implementation
        """
        queryset = self.queryset
        fns = (self.name_filter, self.limit_filter)
        for fn in fns:
            queryset = fn(queryset)

        return queryset


class VisitListView(AppCreateModelMixin, AppView):
    """
    Page visit listing  end-point  view class.
    """
    queryset = PageVisit.objects.all()
    serializer_class = serializers.PageVisitSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a custom post response with resource url
        @see base class implementation
        """
        data = request.DATA
        data.update(dict(ip_address=serializers.ip_address(request),
                          user_agent=serializers.user_agent(request),
                          api_key=serializers.apikey(request)))

        serializer = self.get_serializer(data=data, files=request.FILES)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            data = dict(url=reverse('visit_detail',
                                    args=[serializer.data['id']],
                                    request=request))
            return Response(data, status=status.HTTP_201_CREATED,
                headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
        Handle post request debug hook
        @see base class implementation
        """
        return self.create(request, *args, **kwargs)


class VisitDetailView(AppView, mixins.RetrieveModelMixin):
    """
    Page visit detail  end-point  view class.
    """
    queryset = PageVisit.objects.all()
    serializer_class = serializers.PageVisitSerializer


def str_to_datetime(arg):
    #@ todo - replace with dateutil conversion, more flexible
    return datetime.datetime.strptime(arg, '%Y-%m-%d %H:%M')


class Wrapper(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class PageDiffView(AppView):
    """
    API endpoint class  that allows page activity
    """
    queryset = PageStatistics.objects.all()
    serializer_class = serializers.PageDiffResponseSerializer
    request_serializer_class = serializers.PageDiffRequestSerializer

    stats_interval = 60

    def datetime_filter(self, qs):
        """
        Filter using a datetime range (from, to)
        """
        serializer = self.request.serializer
        from_time = serializer.cleaned_from_time()
        to_time = serializer.cleaned_to_time()
        if from_time == to_time:
            # either Null or equal
            if settings.USE_SNAPSHOT:
                end_time = timezone.now()
                start_time = end_time - datetime.timedelta(
                        seconds=self.stats_interval)
                qs = qs.filter(snapshot_time__gte=start_time,
                          snapshot_time__lte=end_time)
        else:
            pass  # @TODO missing implementation
        return qs

    def direction_filter(self, qs):
        """
        Filter the diff direction (up, down)
        """
        #@ todo: implement
        return qs

    def get_queryset(self):
        """
        Filter the query based on request parameters
        @see base class implementation
        """
        queryset = self.queryset
        fns = (self.domain_filter,
               self.datetime_filter)
        for fn in fns:
            queryset = fn(queryset)

        return queryset.order_by('snapshot_time')

    def filter_queryset(self, queryset):
        """
        View specific filter execution
        @see base class implemenation
        """
        for backend in self.get_filter_backends():
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list_to_dict(self, page_stats):
        return {page_stat['path']: Wrapper(**page_stat)
                for page_stat in page_stats.statistics}

    def stat_diff(self, start, end):
        deltas = []
        for path, end_page in end.items():
            start_page = start.get(path)
            if start_page:
                obj = Wrapper(change=(end_page.visitors - start_page.visitors),
                        path=path,
                        subject=end_page.subject)
                deltas.append(obj)

        return deltas

    def prepare_data(self, raw_data, direction):

        diff_input = raw_data[-2:]
        start = self.list_to_dict(diff_input[0])
        end = self.list_to_dict(diff_input[1])
        diffs = self.stat_diff(start, end)

        def up(changes):
            return  filter(lambda item: item.change > 0, changes)

        def down(changes):
            return filter(lambda item: item.change < 0, changes)

        def both(changes):
            return diffs

        action_map = dict(zip(('up', 'down', 'both'),
                              (up, down, both)))

        return action_map[direction](diffs)

    def get_objects(self):
        object_list = []
        raw_data = list(self.filter_queryset(self.get_queryset()))
        if raw_data and len(raw_data) > 1:
            direction = self.request.serializer.cleaned_direction()
            object_list = self.prepare_data(raw_data, direction)
        else:
            logger.warn('missing underlying statistics')
        return object_list

    def list(self, request, *args, **kwargs):
        self.object_list = self.get_objects()

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)


@api_view(('GET',))
@permission_classes((IsAuthenticated, ))
def api_root(request, request_format=None):
    return Response({
        'users': reverse('user_list',
                        request=request, format=request_format),
        'domains': reverse('domain_list',
                        request=request, format=request_format),
        'visits': reverse('visit_list',
                        request=request, format=request_format),
        'pagediffs': reverse('page_diffs',
                        request=request, format=request_format)
    })
