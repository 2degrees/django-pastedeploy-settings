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
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp
from nose.tools import eq_

from django_pastedeploy_settings import _DJANGO_UNSUPPORTED_SETTINGS
from django_pastedeploy_settings import BadDebugFlagError
from django_pastedeploy_settings import InvalidSettingValueError
from django_pastedeploy_settings import MissingDjangoSettingsModuleError
from django_pastedeploy_settings import resolve_local_conf_options
from django_pastedeploy_settings import UnsupportedDjangoSettingError

from tests.utils import BaseDjangoTestCase
from tests.utils import get_global_conf
from tests.utils import get_local_conf


class TestSettingsModuleSpecification(BaseDjangoTestCase):

    setup_fixture = False

    def test_existing_module(self):
        global_conf = get_global_conf('read_only_empty_module')
        local_conf = get_local_conf()

        resolve_local_conf_options(global_conf, local_conf)

    def test_non_existing_module(self):
        global_conf = get_global_conf('non_existing_module')
        local_conf = get_local_conf()
        assert_raises(
            ImportError,
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )

    def test_unspecified_module(self):
        global_conf = {'debug': 'true'}
        local_conf = get_local_conf()
        assert_raises(
            MissingDjangoSettingsModuleError,
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )


class TestDebuggingConfiguration(BaseDjangoTestCase):

    def test_debug_in_global_conf(self):
        """Django's "DEBUG" must be set to Paster's "debug"."""
        global_conf = get_global_conf('read_only_empty_module', debug=True)
        local_conf = get_local_conf()
        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        assert_in('DEBUG', local_conf_resolved)
        eq_(local_conf_resolved['DEBUG'], True)

    def test_debug_not_in_global_conf(self):
        global_conf = get_global_conf('read_only_empty_module')
        del global_conf['debug']

        local_conf = get_local_conf()

        assert_raises_regexp(
            BadDebugFlagError,
            'Paste\'s "debug" option must be set in the configuration file',
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )

    def test_DEBUG_in_local_conf(self):
        good_global_conf = get_global_conf('read_only_empty_module')
        bad_local_conf = get_local_conf(DEBUG=True)
        assert_raises_regexp(
            BadDebugFlagError,
            r'Django\'s "DEBUG" setting must not be set in the configuration',
            resolve_local_conf_options,
            good_global_conf,
            bad_local_conf,
            )

    def test_DEBUG_in_settings_module(self):
        """DEBUG must not be set in the Django settings module."""
        global_conf = get_global_conf('debug_settings')
        local_conf = get_local_conf()
        assert_raises_regexp(
            BadDebugFlagError,
            r'Settings modules must not define "DEBUG"',
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )


class TestJSONParsing(object):

    def test_valid_json_values(self):
        global_conf = get_global_conf('read_only_empty_module')
        local_conf = get_local_conf(
            parameter1='value1',
            parameter2={'key': [1, 2]},
            )
        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        assert_in('parameter1', local_conf_resolved)
        eq_(local_conf_resolved['parameter1'], 'value1')

        assert_in('parameter2', local_conf_resolved)
        eq_(local_conf_resolved['parameter2'], {'key': [1, 2]})

    def test_invalid_json_values(self):
        global_conf = get_global_conf('read_only_empty_module')

        local_conf = get_local_conf()
        local_conf['parameter'] = 'unquoted string'

        assert_raises_regexp(
            InvalidSettingValueError,
            r'parameter',
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )


class TestCustomStringSubstitution(object):

    def test_no_substitution(self):
        global_conf = get_global_conf('read_only_empty_module')

        option_name = 'SETTING1'
        option_value = 'value'
        local_conf = get_local_conf(**{option_name: option_value})

        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        eq_(option_value, local_conf_resolved[option_name])

    def test_substituting_existing_global_option(self):
        global_option_name = 'global_option_name'
        global_option_value = 'global_option_value'
        global_conf = get_global_conf(
            'read_only_empty_module',
            **{global_option_name: global_option_value}
            )

        local_conf = get_local_conf()
        local_option_name = 'SETTING1'
        local_option_value = '"The value is ${%s}"' % global_option_name
        local_conf[local_option_name] = local_option_value

        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        eq_(
            'The value is global_option_value',
            local_conf_resolved[local_option_name],
            )

    def test_substituting_non_existing_global_option(self):
        global_conf = get_global_conf('read_only_empty_module')

        local_conf = get_local_conf()
        local_option_name = 'SETTING1'
        global_option_name = 'global_option_name'
        local_option_value = '"The value is ${%s}"' % global_option_name
        local_conf[local_option_name] = local_option_value

        assert_raises_regexp(
            InvalidSettingValueError,
            local_option_name + '.+' + global_option_name,
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )

    def test_escaping(self):
        global_conf = get_global_conf('read_only_empty_module')

        local_conf = get_local_conf()
        option_name = 'SETTING1'
        option_value = '"$${var}"'
        local_conf[option_name] = option_value

        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        eq_('${var}', local_conf_resolved[option_name])

    def test_substitution_done_before_json_conversion(self):
        global_option_name = 'global_option_name'
        global_option_value = '1'
        global_conf = get_global_conf(
            'read_only_empty_module',
            **{global_option_name: global_option_value}
            )

        local_conf = get_local_conf()
        local_option_name = 'SETTING1'
        local_option_value = '${%s}' % global_option_name
        local_conf[local_option_name] = local_option_value

        local_conf_resolved = \
            resolve_local_conf_options(global_conf, local_conf)

        eq_(1, local_conf_resolved[local_option_name])


def test_unsupported_settings():
    global_conf = get_global_conf('read_only_empty_module')

    for setting_name in _DJANGO_UNSUPPORTED_SETTINGS:
        local_conf = get_local_conf(**{setting_name: 'foo'})

        assert_raises_regexp(
            UnsupportedDjangoSettingError,
            setting_name,
            resolve_local_conf_options,
            global_conf,
            local_conf,
            )


def test__file__is_ignored():
    """The __file__ argument must be renamed to paste_configuration_file."""
    global_conf = get_global_conf('read_only_empty_module', __file__='conf.ini')
    local_conf = get_local_conf()

    local_conf_resolved = resolve_local_conf_options(global_conf, local_conf)

    assert_in('paste_configuration_file', local_conf_resolved)
    eq_(local_conf_resolved['paste_configuration_file'], 'conf.ini')


def test_original_local_conf_unchanged():
    global_conf = get_global_conf('read_only_empty_module')
    local_conf = get_local_conf()

    local_conf_copy = local_conf.copy()

    resolve_local_conf_options(global_conf, local_conf)

    eq_(local_conf_copy, local_conf)
