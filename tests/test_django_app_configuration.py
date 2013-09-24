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
import os

from django.core.handlers.wsgi import WSGIHandler
from nose.tools import assert_false
from nose.tools import assert_in
from nose.tools import assert_not_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp
from nose.tools import eq_
from nose.tools import ok_

from django_pastedeploy_settings import get_configured_django_wsgi_app

from tests.utils import BaseDjangoTestCase
from tests.utils import get_global_conf
from tests.utils import get_local_conf
from tests.utils import MockApp


_HERE = os.path.dirname(__file__)
_FIXTURES = os.path.join(_HERE, "mock_django_settings")


class TestWSGIAppRetrieval(BaseDjangoTestCase):

    setup_fixture = False

    def test_default_application(self):
        global_conf = get_global_conf('settings5')
        app = get_configured_django_wsgi_app(global_conf)

        eq_(app.__class__, WSGIHandler)

    def test_custom_application(self):
        global_conf = get_global_conf('settings6')
        app = get_configured_django_wsgi_app(
            global_conf,
            WSGI_APPLICATION='"tests.utils.MOCK_WSGI_APP"',
            )
        ok_(isinstance(app, MockApp))


class TestSettingsStorage(BaseDjangoTestCase):

    setup_fixture = False

    def test_local_conf_option_not_in_settings_module(self):
        global_conf = get_global_conf('empty_module2')
        local_conf = get_local_conf(setting1='String')
        get_configured_django_wsgi_app(global_conf, **local_conf)

        from tests.mock_django_settings import empty_module2

        ok_(hasattr(empty_module2, 'setting1'))
        eq_(empty_module2.setting1, 'String')

    def test_local_conf_option_in_settings_module(self):
        global_conf = get_global_conf('one_member_module')
        local_conf = get_local_conf(MEMBER='FOO')
        get_configured_django_wsgi_app(global_conf, **local_conf)

        from tests.mock_django_settings import one_member_module

        eq_(one_member_module.MEMBER, "MEMBER")
        ok_(len(self.logs['warning']), 1)
        eq_(
            '"MEMBER" will not be overridden in ' \
                'tests.mock_django_settings.one_member_module',
            self.logs['warning'][0],
            )

    def test_local_conf_list_option_in_settings_module(self):
        """
        Additional settings can extend lists or tuples in the original module.

        """
        global_conf = get_global_conf('iterables_module')
        local_conf = get_local_conf(LIST=[8, 9], TUPLE=(6, 7))
        get_configured_django_wsgi_app(global_conf, **local_conf)

        from tests.mock_django_settings import iterables_module

        eq_(iterables_module.LIST, (1, 2, 3, 8, 9))
        eq_(iterables_module.TUPLE, (1, 2, 3, 6, 7))


class TestSettingsModuleSpecification(BaseDjangoTestCase):

    setup_fixture = False

    def test_existing_module(self):
        global_conf = get_global_conf('empty_module')
        local_conf = get_local_conf()
        get_configured_django_wsgi_app(global_conf, **local_conf)

        assert_in('DJANGO_SETTINGS_MODULE', os.environ)
        eq_(
            os.environ['DJANGO_SETTINGS_MODULE'],
            'tests.mock_django_settings.empty_module',
            )

    def test_non_existing_module(self):
        global_conf = get_global_conf('non_existing_module')
        assert_raises(ImportError, get_configured_django_wsgi_app, global_conf)

        assert_not_in('DJANGO_SETTINGS_MODULE', os.environ)
