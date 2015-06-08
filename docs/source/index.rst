Conversion of Paste Deployment configuration to Django settings
===============================================================

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_.
:Latest release: |release|

`Paste Deployment <http://pythonpaste.org/deploy/>`_ is a widely-used system
which has the sole purpose of enabling developers and sysadmins to configure
WSGI applications (like Django) and WSGI servers.

This project dynamically converts Paste Deployment configuration files to
Django settings, offering a much more maintainable way to manage the
configuration of your Django projects.


Features
--------

- Simple, Python-free configuration files. The format used is `INI
  <http://en.wikipedia.org/wiki/INI_file>`_ because `configuration files should
  be declarative, not scripts <http://stackoverflow.com/a/648262>`_.
- Settings can be inherited. For example, you can define your base
  settings in your project's repository, while overriding some from a separate
  file outside your repository.
- Setting values are defined with JSON.
- Variable substitution, allowing you to define a value once and reuse it in
  different settings.
- Integration with `Buildout <http://www.buildout.org/>`_, so that you can
  expose your Django settings to Buildout parts.
- Integration with `Nose <https://nose.readthedocs.org/en/latest/>`_, so that
  you can easily set the Django settings to be used by your test suites.
- Compatible with Python v2.7 and v3, and Django 1.4 or later.


Example
-------

You can keep the following file in your project's repository:

.. code-block:: ini

    # base.ini
    
    [DEFAULT]
    django_settings_module = your_django_project.settings
    
    [app:main]
    use = egg:django-pastedeploy-settings
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "${sqlite_db_path}",
            }
        }

And then have two separate files, one for development and the other for
production, both of which will extend ``base.ini``:

.. code-block:: ini

    # development.ini
    
    [DEFAULT]
    debug = true
    sqlite_db_path = /dev/your-project.db
    
    [app:main]
    use = /your-project-repository/base.ini
    SECRET_KEY = "weak key"
    DEBUG_PROPAGATE_EXCEPTIONS = true

.. code-block:: ini

    # production.ini
    
    [DEFAULT]
    debug = false
    sqlite_db_path = /production/your-project.db
    
    [app:main]
    use = /your-project-repository/base.ini
    SECRET_KEY = "str0ng k3y"


Alternatively, you can keep it all in one file:

.. code-block:: ini

    # settings.ini
    
    [DEFAULT]
    django_settings_module = your_django_project.settings
    
    [app:base]
    use = egg:django-pastedeploy-settings
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "${sqlite_db_path}",
            }
        }
    
    [app:development]
    use = base
    set debug = true
    set sqlite_db_path = /dev/your-project.db
    
    SECRET_KEY = "weak key"
    DEBUG_PROPAGATE_EXCEPTIONS = true
    
    [app:production]
    use = base
    set debug = false
    set sqlite_db_path = /production/your-project.db
    
    SECRET_KEY = "str0ng k3y"


Contents
========

.. toctree::
   :maxdepth: 2
   
   paste-factory
   testing
   buildout-integration
   api
   about
   changelog
   twodwsgi-migration
