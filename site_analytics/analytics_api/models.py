#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.models
    :synopsis: analytics_api models module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
#@TODO - refactor to other applications (i.e. stats)
from django.db import models
from django.contrib.auth.models import User

from analytics_api import validators
from analytics_api import fields


class AppBaseModel(models.Model):
    """
    An abstract base class for application model

    """
    class Meta(object):
        abstract = True
        ordering = ("creation_time",)

    id = models.AutoField(primary_key=True, unique=True)

    creation_time = models.DateTimeField(auto_now_add=True)

    creation_user = fields.create_foreign_key_field(
        User,
        related_name="%(app_label)s_%(class)s_related_creation_user")


class Domain(AppBaseModel):
    """
    A class for storing domain attributes.
    Domains represent publishers for which page analytics are performed
    """
    name = fields.create_char_field()

    def __unicode__(self):
        return u'%s' % self.name


class Page(AppBaseModel):
    """
    A class for storing site page attributes.
    """
    class Meta(AppBaseModel.Meta):
        unique_together = (("domain", "subject"),)

    def __unicode__(self):
        return u'%s' % self.path

    domain = fields.create_foreign_key_field(Domain)

    path = fields.create_path_field(unique=True, db_index=True)
    subject = fields.create_subject_field()
    visitors = models.PositiveIntegerField(default=0)


class PageVisit(AppBaseModel):
    """
    A class for capturing a user page visit
    """
    api_key = fields.create_api_key_field()
    domain = fields.create_domain_char_field()
    path = fields.create_path_field()
    subject = fields.create_subject_field()
    ip_address = fields.create_ip_address_field()
    user_agent = fields.create_user_agent_field()


class PageStatistics(AppBaseModel):
    """
    A class for capturing a snapshot of page visit statistics.
    Each snapshot contains information on the pages for
    which there were page visits between two time periods
    """
    domain = fields.create_domain_char_field()
    snapshot_time = models.DateTimeField(auto_now_add=False,
                                         auto_now=False)
    statistics = fields.create_json_field(
           validators=[validators.page_statistics_field_validator])
