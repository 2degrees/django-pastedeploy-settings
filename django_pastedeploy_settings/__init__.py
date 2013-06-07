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
"""
Utilities to set up Django applications, both in Web and CLI environments.

"""
from json import loads as parse_json
from logging import getLogger
import os

from paste.deploy.loadwsgi import appconfig


__all__ = [
    'BadDebugFlagError',
    'InvalidSettingValueError',
    'MissingDjangoSettingsModuleError',
    'SettingException',
    'UnsupportedDjangoSettingError',
    'get_option_values_parsed',
    'wsgify_django',
    ]


_LOGGER = getLogger(__name__)


def wsgify_django(global_conf, **local_conf):
    """
    Load the Django application for use in a WSGI server.
    
    :raises ImportError: If the Django settings module cannot be imported.
    :raises UnsupportedDjangoSettingError: If ``local_conf`` contains a Django
        setting which is not supported.
    :raises MissingDjangoSettingsModuleError: If the ``django_settings_module``
        option is not set.
    :raises BadDebugFlagError: If Django's ``DEBUG`` is set instead of Paste's
        ``debug``.
    :return: The WSGI application for Django as returned by
        :func:`~django.core.servers.basehttp.get_internal_wsgi_application`.
    
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
    django_settings_module = global_conf.get("django_settings_module")
    if not django_settings_module:
        raise MissingDjangoSettingsModuleError(
            'The "django_settings_module" option is not set',
            )
    
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module
    
    # Attaching the variables to the settings module, at least those which had
    # not been defined.
    # We need the module name for __import__ to work properly:
    # http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    module = django_settings_module.split(".")[-1]
    settings_module = __import__(django_settings_module, fromlist=[module])
    
    _validate_debug_data(global_conf, local_conf, settings_module)
    
    options = _get_local_options(global_conf, local_conf)
    
    for (setting_name, setting_value) in options.items():
        if not hasattr(settings_module, setting_name):
            # The name is not used; let's set it:
            setattr(settings_module, setting_name, setting_value)
        elif isinstance(getattr(settings_module, setting_name), (tuple, list)):
            # The name is already used by a list; let's extended it:
            iterable_setting_value = getattr(settings_module, setting_name)
            new_tuple = tuple(iterable_setting_value) + tuple(setting_value)
            setattr(settings_module, setting_name, new_tuple)
        else:
            # The name is already used and it's not a list; let's warn the user:
            _LOGGER.warn(
                '"%s" will not be overridden in %s',
                setting_name,
                django_settings_module,
                )


#{ Type casting


# TODO: The following settings should be supported:
_DJANGO_UNSUPPORTED_SETTINGS = frozenset([
    "FILE_UPLOAD_PERMISSIONS",
    "LANGUAGES",
    "MESSAGE_TAGS",
    ])


def _validate_debug_data(global_conf, local_conf, settings_module):
    if hasattr(settings_module, 'DEBUG'):
        raise BadDebugFlagError(
            'Settings modules must not define "DEBUG". It must be set in the '
                'PasteDesploy configuration file as "debug".',
            )
    
    if "DEBUG" in global_conf or "DEBUG" in local_conf:
        raise BadDebugFlagError(
            'Django\'s "DEBUG" setting must not be set in the configuration '
                'file; use Paste\'s "debug" instead',
            )
    
    if "debug" not in global_conf:
        raise BadDebugFlagError(
            'Paste\'s "debug" option must be set in the configuration file',
            )
    

def _get_local_options(global_conf, local_conf):
    """
    Build the final options based on PasteDeploy's ``global_conf`` and
    ``local_conf``.
    
    """
    local_conf['DEBUG'] = global_conf['debug']
    
    for option_name in local_conf:
        if option_name in _DJANGO_UNSUPPORTED_SETTINGS:
            raise UnsupportedDjangoSettingError(
                "Django setting %s is not (yet) supported; you have to define "
                    "it in your Python settings module." % option_name,
                )

    options = get_option_values_parsed(local_conf)
    
    # We should not import a module with "__file__" as a global variable:
    options['paste_configuration_file'] = global_conf.get("__file__")
    
    return options


def get_option_values_parsed(raw_options):
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


#}
