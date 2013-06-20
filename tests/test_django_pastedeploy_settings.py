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
from json import dumps as convert_to_json
import os

from django.core.handlers.wsgi import WSGIHandler
from nose.tools import assert_false
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp
from nose.tools import eq_
from nose.tools import ok_

from django_pastedeploy_settings import BadDebugFlagError
from django_pastedeploy_settings import InvalidSettingValueError
from django_pastedeploy_settings import get_configured_django_wsgi_app
from django_pastedeploy_settings import MissingDjangoSettingsModuleError
from django_pastedeploy_settings import UnsupportedDjangoSettingError
from django_pastedeploy_settings import _DJANGO_UNSUPPORTED_SETTINGS

from tests.utils import BaseDjangoTestCase
from tests.utils import MockApp

_HERE = os.path.dirname(__file__)
_FIXTURES = os.path.join(_HERE, "mock_django_settings")


class TestDjangoWsgifytor(BaseDjangoTestCase):
    
    setup_fixture = False
    
    def test_debug_flag_source(self):
        """
        The "debug" flag from the global_conf takes precedence over local_conf.
        
        """
        global_conf = _get_global_conf('settings3', debug=False)
        get_configured_django_wsgi_app(global_conf, debug="true")
        
        from django.conf import settings
        assert_false(settings.DEBUG)
    
    def test_local_conf(self):
        global_conf = _get_global_conf('settings4', debug=False)
        get_configured_django_wsgi_app(global_conf, FOO="10")
        
        from django.conf import settings
        eq_(settings.FOO, 10)
    
    def test_default_application(self):
        global_conf = _get_global_conf('settings5', debug=False)
        app = get_configured_django_wsgi_app(global_conf)
        
        eq_(app.__class__, WSGIHandler)
    
    def test_custom_application(self):
        global_conf = _get_global_conf('settings6', debug=False)
        app = get_configured_django_wsgi_app(
            global_conf,
            WSGI_APPLICATION='"tests.utils.MOCK_WSGI_APP"',
            )
        ok_(isinstance(app, MockApp))


class TestSettingUpSettings(BaseDjangoTestCase):
    
    setup_fixture = False
    
    def test_django_settings_module_set_in_environ(self):
        global_conf = _get_global_conf('empty_module')
        local_conf = _get_local_conf()
        get_configured_django_wsgi_app(global_conf, **local_conf)
        eq_(
            os.environ['DJANGO_SETTINGS_MODULE'],
            'tests.mock_django_settings.empty_module',
            )
    
    def test_no_initial_settings(self):
        """
        Additional settings must be added even if there's no initial settings.
        
        """
        global_conf = _get_global_conf('empty_module2')
        local_conf = _get_local_conf(setting1=None, setting2='String')
        get_configured_django_wsgi_app(global_conf, **local_conf)

        from tests.mock_django_settings import empty_module2
        
        ok_(hasattr(empty_module2, 'setting1'))
        ok_(hasattr(empty_module2, 'setting2'))
        eq_(empty_module2.setting1, None)
        eq_(empty_module2.setting2, 'String')
    
    def test_name_clash(self):
        """
        Additional settings must not override initial values in settings.py.
        
        """
        global_conf = _get_global_conf('one_member_module')
        local_conf = _get_local_conf(MEMBER='FOO')
        get_configured_django_wsgi_app(global_conf, **local_conf)
        
        from tests.mock_django_settings import one_member_module
        
        eq_(one_member_module.MEMBER, "MEMBER")
        ok_(len(self.logs['warning']), 1)
        eq_(
            '"MEMBER" will not be overridden in ' \
                'tests.mock_django_settings.one_member_module',
            self.logs['warning'][0],
            )
    
    def test_list_extension(self):
        """
        Additional settings can extend lists or tuples in the original module.
        
        """
        global_conf = _get_global_conf('iterables_module')
        local_conf = _get_local_conf(LIST=[8, 9], TUPLE=(6, 7))
        get_configured_django_wsgi_app(global_conf, **local_conf)
        
        from tests.mock_django_settings import iterables_module
        
        eq_(iterables_module.LIST, (1, 2, 3, 8, 9))
        eq_(iterables_module.TUPLE, (1, 2, 3, 6, 7))
    
    def test_non_django_settings_module(self):
        """
        A MissingDjangoSettingsModuleError is raised if
        django_settings_module is not set.
        
        """
        global_conf = {
            'debug': "true",
            }
        assert_raises(
            MissingDjangoSettingsModuleError,
            get_configured_django_wsgi_app,
            global_conf,
            )
    
    def test_debug_in_python_configuration(self):
        """DEBUG must not be set in the Django settings module."""
        global_conf = {
            'django_settings_module':
                "tests.mock_django_settings.debug_settings",
            }
        assert_raises_regexp(
            BadDebugFlagError,
            r'Settings modules must not define "DEBUG"',
            get_configured_django_wsgi_app,
            global_conf,
            )
    
    def test_non_existing_module(self):
        """
        ImportError must be propagated if the settings module doesn't exist.
        
        """
        global_conf = {
            'debug': "true",
            'django_settings_module': "non_existing_module",
            }
        assert_raises(ImportError, get_configured_django_wsgi_app, global_conf)


class TestSettingsConvertion(object):
    
    def test_valid_json_values(self):
        global_conf = _get_global_conf('empty_module10')
        local_conf = _get_local_conf(
            parameter1='value1',
            parameter2={'key': [1, 2]},
            )
        
        get_configured_django_wsgi_app(global_conf, **local_conf)
        
        from tests.mock_django_settings import empty_module10
        
        ok_(hasattr(empty_module10, 'parameter1'))
        eq_(empty_module10.parameter1, 'value1')
        
        ok_(hasattr(empty_module10, 'parameter2'))
        eq_(empty_module10.parameter2, {'key': [1, 2]})
    
    def test_invalid_json_values(self):
        global_conf = _get_global_conf('empty_module4')
        local_conf = _get_local_conf()
        local_conf['parameter'] = 'unquoted string'
        assert_raises_regexp(
            InvalidSettingValueError,
            r"parameter",
            get_configured_django_wsgi_app,
            global_conf,
            **local_conf
            )
    
    def test_unsupported_settings(self):
        for setting_name in _DJANGO_UNSUPPORTED_SETTINGS:
            global_conf = _get_global_conf('empty_module9')
            local_conf = _get_local_conf(**{setting_name: 'foo'})
            
            assert_raises_regexp(
                UnsupportedDjangoSettingError,
                setting_name,
                get_configured_django_wsgi_app,
                global_conf,
                **local_conf
                )
    
    def test__file__is_ignored(self):
        """The __file__ argument must be renamed to paste_configuration_file."""
        global_conf = _get_global_conf('empty_module3', __file__='config.ini')
        local_conf = _get_local_conf()
        
        get_configured_django_wsgi_app(global_conf, **local_conf)
        
        from tests.mock_django_settings import empty_module3
        
        ok_(hasattr(empty_module3, "paste_configuration_file"))
        eq_(empty_module3.paste_configuration_file, "config.ini")
    
    def test_debug_in_ini_config(self):
        """Django's DEBUG must not be set in the .ini configuration file."""
        exception_message_regexp = \
            r'Django\'s "DEBUG" setting must not be set in the configuration'
        
        bad_global_conf = _get_global_conf('empty_module5', DEBUG='true')
        good_local_conf = _get_local_conf()
        assert_raises_regexp(
            BadDebugFlagError,
            exception_message_regexp,
            get_configured_django_wsgi_app,
            bad_global_conf,
            **good_local_conf
            )
        
        good_global_conf = _get_global_conf('empty_module6')
        bad_local_conf = _get_local_conf(DEBUG=True)
        assert_raises_regexp(
            BadDebugFlagError,
            exception_message_regexp,
            get_configured_django_wsgi_app,
            good_global_conf,
            **bad_local_conf
            )
    
    def test_pastes_debug(self):
        """Django's "DEBUG" must be set to Paster's "debug"."""
        global_conf = _get_global_conf('empty_module8')
        local_conf = _get_local_conf()
        get_configured_django_wsgi_app(global_conf, **local_conf)
        
        from tests.mock_django_settings import empty_module8
        
        ok_(hasattr(empty_module8, 'DEBUG'))
        eq_(empty_module8.DEBUG, True)
    
    def test_no_paste_debug(self):
        """Ensure the "debug" option for Paste is set."""
        global_conf = _get_global_conf('empty_module7')
        del global_conf['debug']
        assert_raises_regexp(
            BadDebugFlagError,
            'Paste\'s "debug" option must be set in the configuration file',
            get_configured_django_wsgi_app,
            global_conf,
            )


#{ Utilities


def _get_global_conf(settings_module_name, debug=True, **extra_options):
    settings_module_path = \
        'tests.mock_django_settings.%s' % settings_module_name
    global_conf = {
        'debug': convert_to_json(debug),
        'django_settings_module': settings_module_path,
        }
    global_conf.update(extra_options)
    return global_conf


def _get_local_conf(**extra_options):
    local_conf = {'SECRET_KEY': 'secret'}
    local_conf.update(extra_options)
    
    local_conf_with_json_values = {}
    for (key, value) in local_conf.items():
        local_conf_with_json_values[key] = convert_to_json(value)
    
    return local_conf_with_json_values


#}
