#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics.log
    :synopsis: logging configuration module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""
import os
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INFO_LOG_LEVEL = 'INFO'
ERROR_LOG_LEVEL = 'ERROR'
DEBUG_LOG_LEVEL = 'DEBUG'

LOG_LEVEL = DEBUG_LOG_LEVEL

_verbose_format = ('%(levelname)s %(asctime)s'
                   + ' %(module)s %(process)d'
                   + ' %(thread)d %(message)s')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': _verbose_format
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': DEBUG_LOG_LEVEL,
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': DEBUG_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'log_file': {
            'level': DEBUG_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(_BASE_DIR, 'django.log'),
            'maxBytes': 16777216,  # 16megabytes
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': ERROR_LOG_LEVEL,
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        'django.db': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': LOG_LEVEL,
            'propagate': True
        },
        'analytics_api': {
            'handlers': ['log_file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True
        },
    }
}
