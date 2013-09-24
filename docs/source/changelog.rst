========
Releases
========

Version 1.0 Release Candidate 2 (2013-09-24)
============================================

- Introduced new syntax to do variable substitution (``${variable_name}``).
- Introduced the function
  :func:`~django_pastedeploy_settings.resolve_local_conf_options`.


Version 1.0 Release Candidate 1 (2013-06-20)
============================================

- Renamed function ``wsgify_django`` to
  :func:`django_pastedeploy_settings.get_configured_django_wsgi_app`.
- Made the :doc:`Nose plugin <testing>` work with multiple databases as
  supported by Django >= 1.3.
- Renamed command-line argument for the PasteDeploy configuration file in the
  :doc:`Nose plugin <testing>` from ``--with-django-wsgified`` to
  ``--paste-deploy-config``.


Version 1.0 Beta 1 (2013-06-19)
===============================

This is the first public release.

**django-pastedeploy-settings** started as a fork of `twod.wsgi
<http://pythonhosted.org/twod.wsgi/>`_ v1, with the sole purpose of managing
Django settings as opposed to all the other functionality supported by
*twod.wsgi*. Information about how to migrate from *twod.wsgi* can be found in
:doc:`twodwsgi-migration`.
