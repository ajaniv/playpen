#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics.test_settings
    :synopsis: test  configuration module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
from .settings import *  # @UnusedWildImport

FORCE_DEBUG = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
USE_SNAPSHOT = True
