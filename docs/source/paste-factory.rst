==========================================
PasteDeploy Application Factory for Django
==========================================

`Paste <http://pythonpaste.org/>`_ is an umbrella project for widely used
WSGI-related packages, as well as the name of a meta-framework part of that
project. One of these projects is `PasteDeploy
<http://pythonpaste.org/deploy/>`_, which offers a very flexible
configuration mechanism (based on `INI files
<http://en.wikipedia.org/wiki/INI_file>`_) to set up your application which
can also give you full control over this initialisation by means of Python code.
It's not only used to set up the application in deployment mode, but also in
development mode.

The way it works is very simple: You define a callable which takes all the
configuration options as arguments and returns a WSGI application object (which
in this case would be a Django application). These callables are called
"Application Factories", and this library provides one you can use in most cases
or even extend when you do something more complicated.

The following is a minimal configuration file which uses the Application Factory
provided by *django-pastedeploy-settings*. You can also :download:`download
a complete example <_static/simplest-settings.ini>`.

.. code-block:: ini

    [DEFAULT]
    debug = false
    django_settings_module = your_django_project.settings
    
    [app:main]
    use = egg:django-pastedeploy-settings

It does not define any option that can be used by Django or your application,
apart from ``debug``. Note this option is lower case: That's the de-facto
spelling for this variable in the WSGI world. *django-pastedeploy-settings* will
automatically set Django's ``DEBUG`` to that value.

Sections with the ``app:`` prefix contain the settings for WSGI applications.
Whenever you reference a PasteDeploy file, you have to specify the application
to be used, or else it'll default to ``main`` (if it exists). All the options
defined in the specified ``app:*`` section will be converted to Django settings,
with the values converted from JSON (except for the options ``use`` and
``paste.app_factory`` which are only used by PasteDeploy).

The ``DEFAULT`` section is special. There you can define variables to be
substituted in other sections, as well as some meta variables for Paste,
*django-pastedeploy-settings* or other 3rd party software. The values set in
this section are never parsed as JSON strings; they'll always be raw strings
and therefore don't need to be quoted.

You can have more than one set of settings for your Django application. If,
for example, you wanted to be able to use your application in development and
deployment mode, you could use a configuration like this:

.. code-block:: ini

    [DEFAULT]
    debug = false
    django_settings_module = your_django_project.settings
    
    [app:main]
    use = egg:django-pastedeploy-settings
    
    [app:development]
    use = main
    set debug = true

Because we need to toggle the value of ``DEBUG`` from the configuration file,
you must remove this variable from your settings module. If you have variables
which depend on this value, you can still refer to it like this:

.. code-block:: ini

    [DEFAULT]
    debug = false
    django_settings_module = your_django_project.settings
    
    [app:main]
    use = egg:django-pastedeploy-settings
    TEMPLATE_DEBUG = %(debug)s
    
    [app:development]
    use = main
    set debug = true
    
Or, you can override them on a per application basis:

.. code-block:: ini

    [DEFAULT]
    debug = false
    django_settings_module = your_django_project.settings
    
    [app:main]
    use = egg:django-pastedeploy-settings
    TEMPLATE_debug = false
    
    [app:development]
    use = main
    set debug = true
    # TEMPLATE_DEBUG will be false unless we override it:
    TEMPLATE_debug = true


You can then use the values the same way you've been doing it, with Django's
``settings`` object or the old way (importing your settings module directly)::

    from django.conf import settings
    
    print settings.DEBUG

This mechanism can be used to complement your settings module or replace it
completely (as long as you don't use `unsupported settings`_, which must still
be set in Python code). The author believes it's best to move
it all to the convenient INI file, except for those settings which are not
really settings, but a crucial element of your application (e.g.,
``TEMPLATE_LOADERS``, ``MIDDLEWARE_CLASSES``, ``FILE_UPLOAD_HANDLERS``,
``INSTALLED_APPS``).


Unsupported settings
====================

Only those settings whose values can be represented with JSON can be defined
in a INI file, which covers the vast majority of settings in Django. The
following are examples of settings whose values cannot be represented in JSON:

- ``FILE_UPLOAD_PERMISSIONS`` (octal number).
- ``LANGUAGES`` (iterable containing results from function calls).

If you need to use them, you would have to define them in your settings
module or :ref:`create your own factory <custom-factory>` to convert the values
by yourself.


Implicit Variables
==================

There are a couple of variables defined by PasteDeploy which you can refer to
in your configuration.

One of them is ``here``, which is the absolute path to the directory that
contains the INI file. You can use it like this:

.. code-block:: ini

    # (...)
    
    [app:main]
    use = egg:django-pastedeploy-settings
    MEDIA_ROOT = %(here)s/media
    
    # (...)

The other variable is ``__file__``, which is the absolute path to the INI
file. It's not very useful in the context of these files, but can be useful
when `using custom factories`_.


Serving Your Application
========================

Serving your application is a piece of cake now that you use PasteDeploy. It's
simpler than using Django's mechanisms because there's no need to import
:mod:`os` and set an environment variable.


Production Server
-----------------

The following is a sample WSGI script for *mod_wsgi*::

    from paste.deploy import loadapp
    
    application = loadapp("config:/path/to/your/config.ini")

And the following is a sample script for FastCGI::

    from paste.deploy import loadapp
    from flup.server.fcgi_fork import WSGIServer
    
    app = loadapp("config:/path/to/your/config.ini")
    WSGIServer(app).run()

You might want to check the deployment documentation for the other Python
frameworks (e.g., Pylons). They've been using WSGI heavily since day one,
so it's likely you'll get ideas on how to meet your special needs, should you
have any.


Development Server
------------------

PasteDeploy makes it easy to use any WSGI-compatible server for development
too, and some Python-based servers (e.g., Gunicorn, PasteScript) make it even
easier thanks to their built-in integration with PasteDeploy. So now you have
the choice of sticking to Django's ``manage renserver`` or use a different one.

There are a few WSGI servers that are very convenient for development of WSGI
application and `PasteScript <http://pythonpaste.org/script/>`_ is by far the
most widely used one. `Unlike Django's
<http://code.djangoproject.com/ticket/3357>`_, it is multi-threaded and
therefore suitable for AJAX interfaces. Like Django's, it's able to reload the
application when you change something in your code. It's also so robust that
it's often the server of choice for people deploying with FastCGI.

Once you have installed PasteScript (e.g., :command:`easy_install PasteScript`),
you need to configure the server in your configuration file by adding the
following section anywhere:

.. code-block:: ini

    [server:main]
    use = egg:Paste#http
    port = 8080

And then you'll be able to run the server::

    cd /path/to/your/project
    paster serve --reload config.ini

:command:`paster` will load the application defined in ``app:main``. If you
want to use a different one, you'd need to set it explicitly, e.g.::

    paster serve --reload config.ini#develop

If you don't want to type that long command all the time, you could just
`execute that file directly <http://pythonpaste.org/script/#scripts>`_.


Configure logging
~~~~~~~~~~~~~~~~~

You can configure logging from the same PasteDeploy configuration file by
adding all `the sections recognized by Python's built-in logging mechanisms
<http://docs.python.org/library/logging.html#configuration-file-format>`_.

A full development configuration file could look like this:

.. code-block:: ini
    
    [server:main]
    use = egg:Paste#http
    port = 8000
    
    [app:main]
    use = config:base-config.ini
    set debug = true
    
    # ===== LOGGING
    
    [loggers]
    keys = root,yourpackage
    
    [handlers]
    keys = global,yourpackage
    
    [formatters]
    keys = generic
    
    # Loggers
    
    [logger_root]
    level = WARNING
    handlers = global
    
    [logger_yourpackage]
    qualname = coolproject.module
    handlers = yourpackage
    propagate = 0
    
    # Handlers
    
    [handler_global]
    class = StreamHandler
    args = (sys.stderr,)
    level = NOTSET
    formatter = generic
    
    [handler_yourpackage]
    class = handlers.RotatingFileHandler
    args = ("%(here)s/logs/coolpackage.log", )
    level = NOTSET
    formatter = generic
    
    # Formatters
    
    [formatter_generic]
    format = %(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %Y-%m-%d %H:%M:%S


Making :command:`manage` work again
===================================

You'll find that your :command:`manage` command will be broken after moving
settings over to a PasteDeploy configuration file. The fix is really simple,
just put the following at the top of your :command:`manage` script::

    from paste.deploy import loadapp
    
    loadapp("config:/path/to/your/configuration.ini")

If the URI varies depending on whether you're in a development environment or
some other condition, you have two ways of setting this URI:

- Using a relative path.
- Introducing some form of variable substitution, such as creating ``manage.py``
  from a template (potentially generated by a build system like Buildout) or
  using an environment variable.


Multiple configuration files
============================

As we've seen so far, PasteDeploy configuration files can be extended in a
cascade like fashion. This can also be done across files.

You could have the following base configuration file:

.. code-block:: ini

    # base-config.ini
    
    [DEFAULT]
    debug = false
    
    [app:base]
    use = egg:django-pastedeploy-settings
    EMAIL_PORT = 25
    
    [app:debug]
    use = base
    set debug = true

And then override it for development:

.. code-block:: ini

    # develop.ini
    
    [server:main]
    use = egg:Paste#http
    port = 8080
    
    [app:main]
    use = config:base-config.ini#debug
    EMAIL_PORT = 1025

This way, you could also run :command:`paster` as::

    paster serve --reload develop.ini


.. _custom-factory:

Using custom factories
======================

If you need to perform a one-off routine when your application is started up
(i.e., before any request) or wrap your Django application with WSGI middleware,
you can write your own PasteDeploy application factory::

    from django_pastedeploy_settings import wsgify_django
    
    
    def make_application(global_config, **local_conf):
        
        # Do something before importing Django and your settings have been applied.
        
        app = wsgify_django(global_config, **local_conf)
        
        # Do something right after your application has been set up (e.g., add WSGI middleware).
        
        return app

``global_config`` is a dictionary that contains all the options in the
``DEFAULT`` section, while ``local_conf`` will contain all the options in the
``app:*`` section. The values in both dictionaries are the raw strings defined
in your INI file, not the decoded JSON values, so if you want to use such
values, you should do it via :data:`django.conf.settings` after calling
:func:`~django_pastedeploy_settings.wsgify_django`. If you need to use any of
those values before calling :func:`~django_pastedeploy_settings.wsgify_django`,
you'd have to decode them yourself (keeping in mind that not all values
are encoded in JSON).

PasteDeploy offers two options to use application factories in a configuration
file:

- **Setuptools entry point**: If you add the following to your :file:`setup.py`
  file::
  
      setup(
          "yourdistribution",
          # (...)
          entry_points="""
          # -*- Entry points: -*-
          [paste.app_factory]
          main = yourpackage.module:make_application
          """,
          )
   
  you'd be able to use the factory as:
  
  .. code-block:: ini
  
      # (...)
      [app:main]
      use = egg:yourdistribution
      # (...)
   
- If you can't or don't want to define an entry point, you can use it like this:

  .. code-block:: ini
  
      # (...)
      [app:main]
      paste.app_factory = yourpackage.module:make_application
      # (...)
