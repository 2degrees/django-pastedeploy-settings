# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2015, 2degrees Limited.
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
Utilities to set up Django applications, both in Web and CLI environments.

"""
from json import loads as parse_json
from logging import getLogger
import os
import re

from paste.deploy.loadwsgi import appconfig


# The order is important to Sphinx' autodoc extension.
__all__ = [
    'resolve_local_conf_options',
    'get_configured_django_wsgi_app',
    'BadDebugFlagError',
    'InvalidSettingValueError',
    'MissingDjangoSettingsModuleError',
    'SettingException',
    'UnsupportedDjangoSettingError',
    ]


_LOGGER = getLogger(__name__)


_OPTION_REFERENCE_REGEX = re.compile(r"""
    (?P<escape_character>\$)?
    \$
    \{
    (?P<referenced_option_name>.+?)
    \}
    """,
    re.VERBOSE,
    )


def resolve_local_conf_options(global_conf, local_conf):
    """
    Return the final values for the items in ``local_conf``.

    :raises ImportError: If the Django settings module cannot be imported.
    :raises UnsupportedDjangoSettingError: If ``local_conf`` contains a Django
        setting which is not supported.
    :raises MissingDjangoSettingsModuleError: If the ``django_settings_module``
        option is not set.
    :raises BadDebugFlagError: If Django's ``DEBUG`` is set instead of Paste's
        ``debug``.
    :return: ``local_conf`` with its values deserialized from JSON and
        variable references resolved
    :rtype: :class:`dict`

    The result also includes the following items:

    - ``DEBUG``: Copied from ``global_conf['debug']``.
    - ``paste_configuration_file``: The path to the PasteDeploy configuration
      file used.

    """
    _validate_debug_data(global_conf, local_conf)
    _require_supported_options_only(local_conf)

    local_conf = dict(local_conf, DEBUG=global_conf['debug'])
    local_conf_resolved = \
        _get_option_values_dereferenced(global_conf, local_conf)
    local_conf_resolved = _get_option_values_parsed(local_conf_resolved)

    # Make the PasteDeploy configuration file path available
    local_conf_resolved['paste_configuration_file'] = \
        global_conf.get('__file__')

    return local_conf_resolved


def get_configured_django_wsgi_app(global_conf, **local_conf):
    """
    Load the Django application for use in a WSGI server.

    :return: The WSGI application for Django as returned by
        :func:`~django.core.servers.basehttp.get_internal_wsgi_application`.

    Internally, this uses :func:`resolve_local_conf_options` and stores the
    result as Django settings. Any exceptions raised by that function are also
    propagated.

    """
    _set_up_settings(global_conf, local_conf)

    return _get_django_wsgi_app()


def _get_django_wsgi_app():
    # The following module can only be imported after the settings have been
    # set.
    from django.core.servers.basehttp import get_internal_wsgi_application
    wsgi_application = get_internal_wsgi_application()
    return wsgi_application


def _set_up_settings(global_conf, local_conf):
    """
    Add the PasteDeploy options ``global_conf`` and ``local_conf`` to the
    Django settings module.

    """
    django_settings_module = \
        _get_django_settings_module_from_global_conf(global_conf)

    _set_django_settings_module(django_settings_module)

    options = resolve_local_conf_options(global_conf, local_conf)
    _store_django_settings(options, django_settings_module)


def _set_django_settings_module(django_settings_module):
    django_settings_module_name = django_settings_module.__name__
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module_name


def _get_django_settings_module_from_global_conf(global_conf):
    django_settings_module_name = global_conf.get('django_settings_module')

    if not django_settings_module_name:
        raise MissingDjangoSettingsModuleError(
            'The "django_settings_module" option is not set',
            )

    django_settings_module = _get_module(django_settings_module_name)
    return django_settings_module


def _get_module(module_qualified_name):
    # We need the module name for __import__ to work properly:
    # http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    module_name = module_qualified_name.split('.')[-1]
    module = __import__(module_qualified_name, fromlist=[module_name])
    return module


def _store_django_settings(settings_dict, django_settings_module):
    for (setting_name, setting_value) in settings_dict.items():
        try:
            existing_setting_value = \
                getattr(django_settings_module, setting_name)
        except AttributeError:
            setattr(django_settings_module, setting_name, setting_value)
        else:
            if isinstance(existing_setting_value, (tuple, list)):
                new_tuple = tuple(existing_setting_value) + tuple(setting_value)
                setattr(django_settings_module, setting_name, new_tuple)
            else:
                # The name is already used and it's not an iterable
                _LOGGER.warn(
                    '"%s" will not be overridden in %s',
                    setting_name,
                    django_settings_module.__name__,
                    )


# Built-in Django settings not currently supported by this plugin
_DJANGO_UNSUPPORTED_SETTINGS = frozenset([
    "FILE_UPLOAD_PERMISSIONS",
    "LANGUAGES",
    "MESSAGE_TAGS",
    ])


def _validate_debug_data(global_conf, local_conf):
    django_settings_module = \
        _get_django_settings_module_from_global_conf(global_conf)
    if hasattr(django_settings_module, 'DEBUG'):
        raise BadDebugFlagError(
            'Settings modules must not define "DEBUG". It must be set in the '
                'PasteDesploy configuration file as "debug".',
            )

    if 'DEBUG' in local_conf:
        raise BadDebugFlagError(
            'Django\'s "DEBUG" setting must not be set in the configuration '
                'file; use Paste\'s "debug" instead',
            )

    if "debug" not in global_conf:
        raise BadDebugFlagError(
            'Paste\'s "debug" option must be set in the configuration file',
            )


def _require_supported_options_only(local_conf):
    for option_name in local_conf:
        if option_name in _DJANGO_UNSUPPORTED_SETTINGS:
            raise UnsupportedDjangoSettingError(
                "Django setting %s is not (yet) supported; you have to define "
                    "it in your Python settings module." % option_name,
                )


def _get_option_values_dereferenced(global_conf, local_conf):
    options = {}
    for local_option_name, local_option_value in local_conf.items():
        try:
            local_option_value_dereferrenced = _OPTION_REFERENCE_REGEX.sub(
                lambda match: _resolve_option_reference(match, global_conf),
                local_option_value,
                )
        except _NonExistingReferencedOptionError as exc:
            raise InvalidSettingValueError(
                'Option "%s" references non-existing global option "%s"' % (
                    local_option_name,
                    exc,
                    ),
                )

        options[local_option_name] = local_option_value_dereferrenced

    return options


def _resolve_option_reference(reference_match, options):
    is_escaping = bool(reference_match.group('escape_character'))
    if is_escaping:
        replacement = reference_match.group(0)[1:]
    else:
        referenced_option_name = reference_match.group('referenced_option_name')
        try:
            referenced_option_value = options[referenced_option_name]
        except KeyError:
            raise _NonExistingReferencedOptionError(referenced_option_name)
        replacement = referenced_option_value

    return replacement


def _get_option_values_parsed(raw_options):
    options = {}
    for (option_name, option_value) in raw_options.items():
        try:
            decoded_option_value = parse_json(option_value)
        except ValueError:
            raise InvalidSettingValueError(
                'Could not decode value for option %r: %r' % (
                    option_name,
                    option_value,
                    ),
                )
        options[option_name] = decoded_option_value
    return options


#{ Exceptions


class SettingException(Exception):
    pass


class BadDebugFlagError(SettingException):
    pass


class MissingDjangoSettingsModuleError(SettingException):
    pass


class UnsupportedDjangoSettingError(SettingException):
    pass


class InvalidSettingValueError(SettingException):
    pass


class _NonExistingReferencedOptionError(InvalidSettingValueError):
    pass


#}
