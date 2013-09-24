##############################################################################
#
# Copyright (c) 2013, 2degrees Limited.
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
from deployrecipes import ConfvarsRecipe

from django_pastedeploy_settings import resolve_local_conf_options


__all__ = ['DecodedConfvarsRecipe']


class DecodedConfvarsRecipe(ConfvarsRecipe):
    """
    Recipe to make PasteDeploy-based Django settings available to Buildout.

    Each setting value must be converted from JSON to ASCII strings.

    """

    @staticmethod
    def get_config_variables_from_app_config(app_config):
        variables = resolve_local_conf_options(
            app_config.global_conf,
            app_config.local_conf,
            )

        variables_with_str_values = {}
        for variable_name, variable_value in variables.items():
            variables_with_str_values[variable_name] = str(variable_value)

        return variables_with_str_values
