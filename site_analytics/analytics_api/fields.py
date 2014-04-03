#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.fields
    :synopsis: Field helper functions module

Common set of helper functions to assist in construction a cohesive bom

.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""


from django.db import models

import jsonfield

from django.core.validators import MinLengthValidator
from analytics_api import validators

NAME_FIELD_MAX_LENGTH = 128
USER_AGENT_FIELD_MAX_LENGTH = 512
SUBJECT_FIELD_MAX_LENGTH = 512
API_KEY_FIELD_MAX_LENGTH = 40


def create_char_field(**kwargs):
    """
    Char field creation utility
    """
    defaults = dict(
        max_length=NAME_FIELD_MAX_LENGTH,
        unique=False,
        db_index=False,
        null=False,
        blank=False)
    defaults.update(kwargs)
    return models.CharField(**defaults)


def create_foreign_key_field(to,
                             **kwargs):
    """
    Foreign key creation utility
    """
    defaults = dict(
                    blank=False,
                    db_constraint=True,
                    null=False,
                    on_delete=models.PROTECT)

    defaults.update(kwargs)
    return models.ForeignKey(to, **defaults)


def create_ip_address_field(**kwargs):
    """
    Create ip address field
    """
    defaults = dict(null=False, blank=False)
    defaults.update(kwargs)
    return  models.GenericIPAddressField(**defaults)


def create_user_agent_field(**kwargs):
    """
    Create user agent field
    """
    defaults = dict(
        null=False,
        blank=False,
        max_length=USER_AGENT_FIELD_MAX_LENGTH,
        validators=[validators.user_agent_field_validator])
    defaults.update(kwargs)
    return  models.CharField(**defaults)


def create_json_field(**kwargs):
    """
    Create json field
    """
    defaults = dict(
        null=False,
        blank=False)
    defaults.update(kwargs)
    return jsonfield.JSONField(**defaults)


def create_path_field(**kwargs):
    """
    Create page path  field
    """
    defaults = dict(
        null=False, blank=False,
        unique=False, db_index=False)
    defaults.update(kwargs)
    return models.URLField(**defaults)


def create_domain_char_field(**kwargs):
    """
    Create domain denormalized  field
    """
    defaults = dict(
        validators=[validators.domain_field_validator])
    defaults.update(kwargs)
    return create_char_field(**defaults)


def create_subject_field(**kwargs):
    """
    Create subject  field
    """
    defaults = dict(
        max_length=512,
        validators=[validators.subject_field_validator])
    defaults.update(kwargs)
    return create_char_field(**defaults)


def create_api_key_field(**kwargs):
    """
    Create api key  field
    """
    defaults = dict(
        max_length=API_KEY_FIELD_MAX_LENGTH,
        validators=[validators.api_key_field_validator,
                    MinLengthValidator(API_KEY_FIELD_MAX_LENGTH)])
    defaults.update(kwargs)
    return create_char_field(**defaults)
