#!/usr/bin/env bash
#
# Common configuration file
#

APP_LIST=( \
        analytics_api \
        rest_framework \
        rest_framework.authtoken \
        )

AUTH_FIXTURE_LIST=( \
    auth.User       \
    auth.Group      \
    authtoken 
    )

APP_FIXTURE_LIST=( \
    analytics_api.Domain \
    analytics_api.PageStatistics \
    
    )



FIXTURE_LIST=(auth "${APP_FIXTURE_LIST[@]}")

MANAGE_CMD="manage.py"
DJANGO_SETTINGS="analytics.settings"
SETTING_ARGS="--settings=$DJANGO_SETTINGS"
DUMPDATA_ARGS="-n --indent 4 -e contenttypes"
VERBOSITY_ARGS="-v 3"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR=${SCRIPT_DIR}/..
FIXTURE_DIR=${ROOT_DIR}/fixtures

VENV_AWS_DIR=/opt/python/run/venv
VENV_LOCAL_DIR=~/pyenv/site_analytics

REST_FRAMEWORK_FIXTURE_LIST=( \
    rest_framework.Token \
    )
