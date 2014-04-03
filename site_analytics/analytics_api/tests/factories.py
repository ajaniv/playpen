#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.tests.factories
    :synopsis: unit test factory module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
import random
import factory
from datetime import timedelta

from django.utils import timezone

from analytics_api import models
from analytics_api import serializers


class UserFactory(factory.DjangoModelFactory):

    FACTORY_FOR = 'auth.User'
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)
    username = 'test_user'

    @staticmethod
    def create_users(count=1, prefix='test_user'):
        users = [UserFactory.create_user(username='%s_%d' % (prefix, index))
            for index in range(1, count + 1)]
        return users

    @staticmethod
    def create_user(username, password=None):
        password = password or username
        user = UserFactory.build(username=username)
        user.set_password(password)
        user.save()
        return user


class TokenFactory(factory.DjangoModelFactory):

    FACTORY_FOR = 'authtoken.Token'
    FACTORY_DJANGO_GET_OR_CREATE = ('user',)


class BaseAppModelFactory(factory.DjangoModelFactory):
    ABSTRACT_FACTORY = True
    FACTORY_FOR = models.AppBaseModel
    FACTORY_DJANGO_GET_OR_CREATE = ('id', )
    creation_user = factory.SubFactory(UserFactory)
    id = factory.Sequence(lambda n:   n)


class DomainFactory(BaseAppModelFactory):
    ABSTRACT_FACTORY = False
    FACTORY_FOR = models.Domain
    FACTORY_DJANGO_GET_OR_CREATE = ('name', )
    name = 'test_domain.com'


class PageFactory(BaseAppModelFactory):
    ABSTRACT_FACTORY = False
    FACTORY_FOR = models.Page

    domain = factory.SubFactory(DomainFactory)

    path = factory.Sequence(
        lambda n: 'http://path_root/path_child/{}'.format(n))
    subject = factory.Sequence(lambda n: 'Subject_{}'.format(n))
    visitors = factory.Sequence(lambda n: n)

    @staticmethod
    def create_pages(page_count=1, domain=None):
        domain = domain or DomainFactory.create()
        pages = [PageFactory.create(domain=domain)
                 for _ in range(page_count)]
        return pages


def make_page_stats(pages, index, direction):
    """
    Create page stats helper function
    """
    if direction == serializers.DELTA_UP:
        make_page_stats.counter += 1
        page_visits = [make_page_stats.counter for _ in range(len(pages))]
        make_page_stats.counter += 1
    elif direction == serializers.DELTA_DOWN:
        page_visits = [make_page_stats.counter
                       for _ in range(len(pages))]
        make_page_stats.counter -= 1
    else:
        page_visits = [random.randint(0, 10) for _ in range(len(pages))]
    stats = [dict(path=page.path, visitors=visitors, subject=page.subject)
               for page, visitors in zip(pages, page_visits)]
    return stats


def init_page_visits(direction, stats_count):
    """
    Reset the function counter cache
    """
    if direction == serializers.DELTA_UP:
        make_page_stats.counter = 1
    elif direction == serializers.DELTA_DOWN:
        make_page_stats.counter = stats_count + 1
    else:
        make_page_stats.counter = 0


class PageStatisticsFactory(BaseAppModelFactory):
    ABSTRACT_FACTORY = False
    FACTORY_FOR = models.PageStatistics
    domain = factory.SubFactory(DomainFactory)

    @staticmethod
    def create_stats(stats_count=1, interval=5,
                     page_count=1, domain_name=None,
                     direction=serializers.DELTA_UP):
        """
        Create page statistic objects
        """
        init_page_visits(direction, stats_count)
        stats_interval = timedelta(seconds=interval)
        snapshot_time = timezone.now() - timedelta(
                    seconds=(interval * stats_count) + 2)
        domain_name = domain_name or DomainFactory.name
        domain = DomainFactory.create(name=domain_name)
        pages = PageFactory.create_pages(page_count, domain)
        current_time = snapshot_time
        stats = []
        for index in range(stats_count):
            page_stats = PageStatisticsFactory.create(
                domain=domain,
                statistics=make_page_stats(pages, index, direction),
                snapshot_time=current_time)
            current_time += stats_interval
            stats.append(page_stats)

        return stats
