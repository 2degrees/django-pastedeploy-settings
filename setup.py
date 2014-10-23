# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2014, 2degrees Limited.
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

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
version = open(os.path.join(here, "VERSION.txt")).readline().rstrip()

setup(
    name="django-pastedeploy-settings",
    version=version,
    description="Conversion of Paste Deployment configuration to Django settings",
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
    keywords="django wsgi paste pastedeploy web webtest nose nosetests",
    author="2degrees Limited",
    author_email="2degrees-floss@googlegroups.com",
    url="http://pythonhosted.org/django-pastedeploy-settings/",
    license="BSD (http://dev.2degreesnetwork.com/p/2degrees-license.html)",
    packages=find_packages(exclude=["tests"]),
    py_modules=["django_testing", "django_testing_recipe"],
    zip_safe=False,
    tests_require=["nose", "coverage"],
    install_requires=[
        "Django >= 1.4",
        "PasteDeploy >= 1.3.3",
        "Paste >= 1.7.2",
        "setuptools",
        ],
    extras_require={
        'nose-buildout': ["zc.recipe.egg >= 1.2.2"],
        'buildout-options': ["deployrecipes >= 1.0"],
        },
    test_suite="nose.collector",
    entry_points="""\
        [paste.app_factory]
        main = django_pastedeploy_settings:get_configured_django_wsgi_app

        [paste.composite_factory]
        full_django = django_pastedeploy_settings.factories:make_full_django_app

        [nose.plugins.0.10]
        paste-deploy-config = django_testing:DjangoPastedeployPlugin

        [zc.buildout]
        nose = django_testing_recipe:DjangoPastedeployRecipe [nose-buildout]
        django-settings = django_pastedeploy_settings.buildout_options:DecodedConfvarsRecipe [buildout-options]
        """,
    )
