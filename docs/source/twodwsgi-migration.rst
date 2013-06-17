========================
Migrating From twod.wsgi
========================

It should be relatively easy to migrate from `twod.wsgi
<http://pythonhosted.org/twod.wsgi/>`_ v1, since both libraries use PasteDeploy
to define Django settings. The main difference is that this library uses JSON
to define the setting values, while *twod.wsgi* v1 required the datatypes to
be specified separately.

In addition to setting **django-pastedeploy-settings** as a dependency of your
Python distribution, you need to do the following all of your INI files:

- Make the ``use`` options refer to ``egg:django-pastedeploy-settings``
  instead of ``egg:twod.wsgi``.
- Convert all the setting values to JSON.
- Remove any typecasting-related options in ``[DEFAULT]`` (i.e.,
  ``twod.booleans``, ``twod.integers``, ``twod.tuples``,
  ``twod.nested_tuples``, ``twod.dictionaries`` and
  ``twod.none_if_empty_settings``).
