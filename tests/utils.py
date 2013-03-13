# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2013, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of django-pastedeploy-settings
# <https://github.com/2degrees/django-pastedeploy-settings>, which is subject
# to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
import logging
import os

import django.conf


__all__ = ("BaseDjangoTestCase", "LoggingHandlerFixture", "MOCK_WSGI_APP",
    "MockApp", "MockLoggingHandler")


class BaseDjangoTestCase(object):
    """
    Base test case to set up and reset the Django settings object.
    
    """
    
    django_settings_module = "tests.mock_django_settings.settings"
    
    setup_fixture = True
    
    def setup(self):
        if self.setup_fixture:
            os.environ['DJANGO_SETTINGS_MODULE'] = self.django_settings_module
        # Setting up the logging fixture:
        self.logging_handler = LoggingHandlerFixture()
        self.logs = self.logging_handler.handler.messages
    
    def teardown(self):
        self.logging_handler.undo()
        django.conf.settings = django.conf.LazySettings()
        if "DJANGO_SETTINGS_MODULE" in os.environ:
            del os.environ['DJANGO_SETTINGS_MODULE']


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected log entries."""
    
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())
    
    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class LoggingHandlerFixture(object):
    """Manager of the :class:`MockLoggingHandler`s."""
    
    def __init__(self):
        self.logger = logging.getLogger("django_pastedeploy_settings")
        self.handler = MockLoggingHandler()
        self.logger.addHandler(self.handler)
    
    def undo(self):
        self.logger.removeHandler(self.handler)


#{ Mock WSGI apps


class MockApp(object):
    """
    Mock WSGI application.
    
    """
    
    def __init__(self, status, headers):
        self.status = status
        self.headers = headers

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response(self.status, self.headers)
        return ["body"]


MOCK_WSGI_APP = MockApp('200 OK', ())


#}
