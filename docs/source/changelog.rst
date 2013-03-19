========
Releases
========

Version 1.0 Alpha 1 (Unreleased)
================================

Initial release, forked from `twod.wsgi <http://pythonhosted.org/twod.wsgi/>`_
v1.

Backwards incompatible changes:

- The PasteDeploy factory used in INI files should be changed from
  ``egg:twod`` to ``egg:django-pastedeploy-settings``.
- In global configuration options (those under ``[DEFAULT]``), the ``"twod."``
  prefix should be replaced with ``"custom_settings."``. So the following
  options should be updated accordingly if used:

  - ``twod.booleans`` to ``custom_settings.booleans``.
  - ``twod.integers`` to ``custom_settings.integers``.
  - ``twod.tuples`` to ``custom_settings.tuples``.
  - ``twod.nested_tuples`` to ``custom_settings.nested_tuples``.
  - ``twod.dictionaries`` to ``custom_settings.dictionaries``.
  - ``twod.none_if_empty_settings`` to
    ``custom_settings.none_if_empty_settings``.
