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

from django_pastedeploy_settings import get_option_values_parsed


__all__ = ['DecodedConfvarsRecipe']


class DecodedConfvarsRecipe(ConfvarsRecipe):
    """
    Recipe to make PasteDeploy-based Django settings available to Buildout.

    """
    
    def get_config_variables(self, *args, **kwargs):
        config_variables_raw = super(DecodedConfvarsRecipe, self) \
            .get_config_variables(*args, **kwargs)
        
        config_variables = get_option_values_parsed(config_variables_raw)
        return config_variables
