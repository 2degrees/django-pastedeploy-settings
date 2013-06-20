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
Buildout recipe to use the Nose plugin
:class:`django_testing.DjangoPastedeployPlugin`.

"""
from zc.buildout import UserError
from zc.recipe.egg import Scripts


class DjangoPastedeployRecipe(Scripts):
    
    def __init__(self, buildout, name, options):
        config_uri = options.pop("paste_config_uri", None)
        if not config_uri:
            raise UserError("Part [%s] must define the PasteDeploy config URI "
                            "in 'paste_config_uri'" % name)
        
        options['initialization'] = _INITIALIZATION % config_uri
        options['arguments'] = "argv=args"
        options['scripts'] = "nosetests"
        super(DjangoPastedeployRecipe, self).__init__(buildout, name, options)


_INITIALIZATION = """
from sys import argv
args = [argv[0], "--paste-deploy-config=%s"] + argv[1:]
"""
