# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2016, 2degrees Limited.
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
"""
Nose plugin to run Django applications in a WSGI environment.

This module has no automated tests on purpose. Functional tests would be very
useful.

"""
from warnings import warn

from nose.plugins import Plugin
from paste.deploy import loadapp


__all__ = ("DjangoPastedeployPlugin",)


class DjangoPastedeployPlugin(Plugin):
    """
    Loads the Django application described by the PasteDeploy configuration URL
    in a WSGI environment suitable for testing.
    
    """
    enabled = False
    
    name = "paste-deploy-config"
    
    enableOpt = "paste_config_uri"
    
    def options(self, parser, env):
        # Mention "Django" in the argument help texts to give more context to
        # the user

        parser.add_option(
            "--%s" % self.name,
            type="string",
            default="",
            dest=self.enableOpt,
            help="Load the Django application described by the PasteDeploy "
                "configuration URI in a WSGI environment suitable for testing.",
            )

        parser.add_option(
            "--no-db",
            action="store_false",
            default=True,
            dest="create_db",
            help="Do not set up a Django test database (deprecated)",
            )

        parser.add_option(
            "--keepdb",
            action="store_true",
            default=False,
            dest="keep_db",
            help="Keep the Django test database between runs",
            )
    
    def configure(self, options, conf):
        """Store the URI to the PasteDeploy configuration."""
        super(DjangoPastedeployPlugin, self).configure(options, conf)

        if not options.create_db:
            warn("--no-db is deprecated in favour of --keepdb")

        self.paste_config_uri = getattr(options, self.enableOpt)
        self.enabled = bool(self.paste_config_uri)
        self.verbosity = options.verbosity
        self.keep_db = not options.create_db or options.keep_db

    def begin(self):
        # Set up the settings before using Django
        loadapp(self.paste_config_uri)
        
        self._set_up_test_environment()
        self._create_test_databases()
    
    def finalize(self, result=None):
        self._remove_test_databases()
        self._tear_down_test_environment()
    
    def _set_up_test_environment(self):
        from django.test.utils import setup_test_environment
        setup_test_environment()
    
    def _tear_down_test_environment(self):
        from django.test.utils import teardown_test_environment
        teardown_test_environment()
    
    def _create_test_databases(self):
        from django.conf import settings
        from django.test.utils import get_runner

        TestRunner = get_runner(settings)
        self.test_runner = \
            TestRunner(self.verbosity, keepdb=self.keep_db, interactive=False)
        self.db_config = self.test_runner.setup_databases()
    
    def _remove_test_databases(self):
        self.test_runner.teardown_databases(self.db_config)
