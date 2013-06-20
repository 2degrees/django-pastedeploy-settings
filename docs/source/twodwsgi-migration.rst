========================
Migrating From twod.wsgi
========================

It should be relatively easy to migrate from `twod.wsgi
<http://pythonhosted.org/twod.wsgi/>`_ v1, since both libraries use PasteDeploy
to define Django settings. The main difference is that this library uses JSON
to define the setting values, while *twod.wsgi* v1 required the datatypes to
be specified separately.

In addition to setting **django-pastedeploy-settings** as a dependency of your
Python distribution, you need to do the following in all of your INI files:

- Make the ``use`` options refer to ``egg:django-pastedeploy-settings``
  instead of ``egg:twod.wsgi``.
- Convert all the setting values to JSON.
- Remove any typecasting-related options in ``[DEFAULT]`` (i.e.,
  ``twod.booleans``, ``twod.integers``, ``twod.tuples``,
  ``twod.nested_tuples``, ``twod.dictionaries`` and
  ``twod.none_if_empty_settings``).

If you have your own PasteDeploy application factory, you need to replace the
call to the function ``twod.wsgi.wsgify_django`` with
:func:`django_pastedeploy_settings.get_configured_django_wsgi_app`.

Finally, if you were using the Builtout recipe that :doc:`integrates
django-pastedeploy-settings and Nose <testing>`, you'll also have to update the
Buildout part that uses it to replace the recipe ``twod.wsgi:nose`` to
``django-pastedeploy-settings:nose``.
