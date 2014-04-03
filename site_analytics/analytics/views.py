#/usr/bin/env python
# -#- coding: utf-8 -#-

#
# Copyright (C) 2013-2014 OndALear LLC
#

# Initial version: 2014-03-22
# Author: Amnon Janiv <amnon.janiv@ondalear.com>


"""

..  module:: analytics.views
    :synopsis: top level analytics views module


.. moduleauthor:: Amnon Janiv <amnon.janiv@ondalear.com>

"""


from django.shortcuts import redirect


def home(request):
    """
    Redirect to home page
    """
    return redirect('/admin/')
