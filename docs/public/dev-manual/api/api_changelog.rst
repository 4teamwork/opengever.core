.. _api-changelog:

API Changelog
=============


2021.2.0 (unreleased)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- No changes yet


Other Changes
^^^^^^^^^^^^^

- No changes yet


2021.1.0 (2021-01-06)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- ``@schema``, ``@types``: Only return ``title_de`` / ``title_fr`` fields if corresponding language is enabled in deployment (see :ref:`docs <translated-titles>`).

- Serialization: Only serialize values for ``title_de`` / ``title_fr`` fields if corresponding language is enabled in deployment (see :ref:`docs <translated-titles>`; applies to Dossiers, Repositoryfolders, and Inboxes).

.. disqus::
