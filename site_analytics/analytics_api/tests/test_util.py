#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics_api.tests.test_util
    :synopsis: test utilities module

An assembly of helper classes mostly derived from open source packages
including tastypie
.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""

#@TODO: complete the implementation

import json
import time
import logging
from functools import wraps
from django.utils.encoding import force_text
from django.conf import settings
from django.test.client import Client
from . import factories


_logger = logging.getLogger(__name__)

DEFAULT_RESPONSE_LIMIT = 10


class ResourceTestCaseMixin(object):
    DEFAULT_USER_NAME = 'test_user'
    DEFAULT_PASSWORD = 'test_user'

    def setUp(self):
        self.user = factories.UserFactory.create_user(username=self.username,
                                          password=self.password)
        self.token = factories.TokenFactory(user=self.user)
        self.api_key = self.token.key
        self.api_client = Client()
        self.limit = DEFAULT_RESPONSE_LIMIT
        self.saved_debug = settings.DEBUG
        try:
            if settings.FORCE_DEBUG:
                settings.DEBUG = True
        except AttributeError:
            pass

    @property
    def username(self):
        return self.get_username()

    def get_username(self):
        return self.DEFAULT_USER_NAME

    @property
    def password(self):
        return self.get_password()

    def get_password(self):
        return  self.DEFAULT_PASSWORD

    def tearDown(self):
        settings.DEBUG = self.saved_debug

    def force_debug(self, value=True):
        settings.DEBUG = value

    def user_agent_header(self):
        return  {'USER_AGENT': 'test client'}

    def create_basic(self, username, password):
        """
        Creates & returns the HTTP ``Authorization`` header for use with BASIC
        Auth.
        """
        import base64
        return 'Basic %s' % base64.b64encode(
                ':'.join([username, password]).encode('utf-8')).decode('utf-8')

    def get_credentials(self):
        return {
            'HTTP_AUTHORIZATION':
                self.create_basic(username=self.username,
                                  password=self.password)
            }


class HttpTestcaseMixin(object):
    """
    A useful base class for HTTP test case validation
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertHttpOK(self, resp):
        """
        Ensures the response is returning a HTTP 200.
        """
        return self.assertEqual(resp.status_code, 200)

    def assertHttpCreated(self, resp):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(resp.status_code, 201)

    def assertHttpAccepted(self, resp):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertTrue(resp.status_code in [202, 204])

    def assertHttpMultipleChoices(self, resp):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(resp.status_code, 300)

    def assertHttpSeeOther(self, resp):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(resp.status_code, 303)

    def assertHttpNotModified(self, resp):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(resp.status_code, 304)

    def assertHttpBadRequest(self, resp):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(resp.status_code, 400)

    def assertHttpUnauthorized(self, resp):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(resp.status_code, 401)

    def assertHttpForbidden(self, resp):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(resp.status_code, 403)

    def assertHttpNotFound(self, resp):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(resp.status_code, 404)

    def assertHttpMethodNotAllowed(self, resp):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(resp.status_code, 405)

    def assertHttpConflict(self, resp):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(resp.status_code, 409)

    def assertHttpGone(self, resp):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(resp.status_code, 410)

    def assertHttpUnprocessableEntity(self, resp):
        """
        Ensures the response is returning a HTTP 422.
        """
        return self.assertEqual(resp.status_code, 422)

    def assertHttpTooManyRequests(self, resp):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(resp.status_code, 429)

    def assertHttpApplicationError(self, resp):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(resp.status_code, 500)

    def assertHttpNotImplemented(self, resp):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(resp.status_code, 501)

    def assertValidJSON(self, data):
        """
        Given the provided ``data`` as a string, ensures that it is valid JSON
        & can be loaded properly.
        """
        # Just try the load. If it throws an exception,
        # the test case will fail.
        self.serializer.from_json(data)

    def assertValidJSONResponse(self, resp):
        """
        Given a ``HttpResponse`` coming back from using the ``client``,
        assert that you get back:

        * An HTTP 200
        * The correct content-type (``application/json``)
        * The content is valid JSON
        """
        self.assertHttpOK(resp)
        self.assertTrue(resp['Content-Type'].startswith('application/json'))
        self.assertValidJSON(force_text(resp.content))

    def assertValidXMLResponse(self, resp):
        """
        Given a ``HttpResponse`` coming back from using the ``client``,
        assert that you get back:

        * An HTTP 200
        * The correct content-type (``application/xml``)
        * The content is valid XML
        """
        self.assertHttpOK(resp)
        self.assertTrue(resp['Content-Type'].startswith('application/xml'))
        self.assertValidXML(force_text(resp.content))

    def deserialize(self, resp):
        """
        Deserialize the response  assuming json content
        """
        return json.loads(resp.content)

    def serialize(self, data, data_format='application/json'):
        """
        Serialize the data into json
        """
        return self.serializer.serialize(data, format=data_format)

    def assertKeys(self, data, expected):
        """
        Compare two key sets
        """
        self.assertEqual(sorted(data.keys()), sorted(expected))


def timeit(method):
    @wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('%r (%r, %r) %2.2f sec' %
              (method.__name__, args, kw, te - ts))
        return result

    return timed


class Timer(object):
    msg = "%s elapsed time: %f ms"

    def __init__(self,  user_msg,  use_clock=True,
                 verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or _logger
        self.extra_msg = user_msg
        self.timer_fn = time.clock if use_clock else time.time

    def __enter__(self):
        self.start = self.now()
        return self

    def __exit__(self, *args):
        self.end = self.now()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs

        if self.verbose:
            self.logger.debug(self.msg, self.extra_msg, self.msecs)

    def now(self):
        return self.timer_fn()
