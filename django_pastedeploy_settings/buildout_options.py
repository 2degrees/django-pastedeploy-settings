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

from django_pastedeploy_settings import _get_option_values_parsed


__all__ = ['DecodedConfvarsRecipe']


class DecodedConfvarsRecipe(ConfvarsRecipe):
    """
    Recipe to make PasteDeploy-based Django settings available to Buildout.

    Each setting value must be converted from JSON to ASCII strings.

    """

    def get_config_variables(self, *args, **kwargs):
        variables_with_json_values = super(DecodedConfvarsRecipe, self) \
            .get_config_variables(*args, **kwargs)

        variables = _get_option_values_parsed(variables_with_json_values)

        variables_with_str_values = {}
        for variable_name, variable_value in variables.items():
            variables_with_str_values[variable_name] = str(variable_value)

        return variables_with_str_values
