#!/usr/bin/env python
import os
from distutils.core import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()


setup(name="analytics",
      version='0.1.0',
      description="Analytics POC",
      long_description='README,md',
      author="Amnon Janiv",
      author_email="amnon.janiv@ondalear.com",
      url="",
      packages=["analytics", "analytics_api", "analytics_api.tests"],
      include_package_data=True,
      license="None",
      classifiers=['Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'],
      )
