========================
PasteDeploy and Buildout
========================

If you're using `Buildout <http://www.buildout.org/>`_, you may want to use
the `zc.recipe.egg:scripts <http://pypi.python.org/pypi/zc.recipe.egg>`_
recipe to preppend the initialisation code to your scripts. It'd be a powerful
tool when your application may be run in different modes (e.g., production,
development). For example, you can use it like this:

.. code-block:: ini

    [buildout]
    parts = scripts
    
    # ...
    
    [scripts]
    recipe = zc.recipe.egg:scripts
    eggs =
        ipython
        YOUR_DISTRIBUTION
        sphinx
    initialization = from paste.deploy import loadapp; loadapp("${vars:config_uri}")
    # "manage" is defined as a distutil entry point in YOUR_DISTRIBUTION
    scripts =
        ipython
        manage
        sphinx-build
    
    [vars]
    config_uri = config:${buildout:directory}/config.ini
    
    # ...


Accessing Django Settings from Buildout Parts
=============================================

In order to avoid duplicating configuration, this library provides a Buildout
recipe (named "django-settings") that makes your Django settings available
to other Buildout parts by loading all the Django settings into the part using
the recipe.

You would use the recipe as follows:

.. code-block:: ini

    # (...)
    
    [vars]
    recipe = django-pastedeploy-settings[buildout-options]:django-settings
    config_uri = config:${buildout:directory}/config.ini
    factory_distribution = YOUR_DISTRIBUTION
    
    # (...)

.. note::

    This recipe requires this library to with installed with the *extra*
    dependency group named "buildout-options".

That will dynamically augment the ``vars`` part with all the Django settings,
so that you can refer to any of those settings by using the syntax
``${vars:DJANGO_SETTING_NAME}`` in other Buildout parts. For example:

.. code-block:: ini

    # (...)
    
    [generate_web_server_config_file]
    recipe = recipe_to_generate_web_server_config_file
    domain_name = ${vars:YOUR_SITE_DOMAIN_NAME}
    
    # (...)
