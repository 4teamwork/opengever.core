opengever.core
==============

.. contents:: Table of Contents

Development installation
------------------------

To get a basic development installation, make sure the dependencies listed
below are satisfied and run the following steps:

.. code::

    $ git clone git@github.com:4teamwork/opengever.core.git
    $ cd opengever.core
    $ ln -s development.cfg buildout.cfg
    $ python bootstrap.py
    $ bin/buildout

Dependencies
~~~~~~~~~~~~

Python 2.7
^^^^^^^^^^

``opengever.core`` requires at least Python 2.7, and using a 64-bit build of
Python is highly recommended.

SQL Database
^^^^^^^^^^^^

``opengever.core`` requires a SQL database to store some configuration.
Before you can configure your first client you need to set up a database.

Currently there are three SQL databases supported:

- **PostgreSQL**

.. code::

    $ brew install postgresql --with-python
    $ brew services start postgresql
    $ brew services run postgresql
    $ createdb opengever

- **MySQL**

.. code::

    $ brew install mysql
    $ mysql -u root
    > CREATE DATABASE opengever CHARACTER SET utf8;
    > GRANT ALL ON opengever.* TO opengever@localhost IDENTIFIED BY 'opengever';
    > FLUSH PRIVILEGES;

- **Oracle**

OpenLDAP 2.x
^^^^^^^^^^^^

The Python `ldap <http://www.python-ldap.org/>`_ module requires the
`OpenLDAP 2.x <http://www.openldap.org/>`_ client libraries.

Java
^^^^

If fulltext indexing using `ftw.tika <https://github.com/4teamwork/ftw.tika>`_
is enabled, Java is required in order to run `tika-server` (at least JRE 1.6
is required for Tika).

LaTeX
^^^^^

A LaTeX distribution and the ``pdflatex`` binary are required for generating
dossier covers, dossier details and dossier listing PDFs as well as open task
reports and task listing PDFs.

For CentOS, the ``tetex-latex`` package contains the ``pdflatex`` binary. For
local development on OS X we recommend the `MacTeX distribution <http://www.tug.org/mactex/>`_.

Additionally, some LaTeX fonts are required. You need at least the Arial font
for LaTeX. Our `internal SVN repo <https://svn.4teamwork.ch/repos/Vorlagen/trunk/latex-fonts/>`_
contains a copy of fonts and installation instructions.

HAProxy
^^^^^^^

For a production installation you need to configure *at least* two Zope
instances per AdminUnit (in order to avoid deadlocks when remote-requests are
executed during tasks across AdminUnits).

To balance load between Zope instances we use `HAProxy <http://www.haproxy.org/>`_.
The configuration is pretty standard:

.. code::

    frontend admin-unit-1
        bind *:10001
        default_backend admin-unit-1

    backend admin-unit-1
      appsession __ac len 32 timeout 1d
      cookie serverid insert nocache indirect
      balance roundrobin
      option httpchk

      server admin-unit-1-01 10.0.0.1:10101 cookie admin-unit-1-01 check inter 10s maxconn 5 rise 1
      server admin-unit-1-02 10.0.0.1:10102 cookie admin-unit-1-02 check inter 10s maxconn 5 rise 1

Apache
^^^^^^

In order to set up a reverse proxy that proxies requests to several HAProxy
frontends we use `Apache <http://httpd.apache.org/>`_.

Postfix
^^^^^^^

Mail-In as well as Mail-Out functionality requires an MTA - we recommend
`Postfix <http://www.postfix.org/>`_. See `ftw.mail <https://github.com/4teamwork/ftw.mail/>`_'s
README for details on how to configure Mail-In.

Perl and ``Email::Outlook::Message`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to convert Outlook ``*.msg`` messages to RFC822 ``*.eml`` when using
Drag&Drop upload, we use the `msgconvert.pl <http://www.matijs.net/software/msgconv/>`_
script. This script requires Perl and the ``Email::Outlook::Message`` module.

So install Perl, ``perl-YAML`` and the following Perl modules:

.. code::

    Email::Outlook::Message
    Email::LocalDelivery
    Getopt::Long
    Pod::Usage


Celery, Erlang and RabbitMQ
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If `opengever.pdfconverter <https://github.com/4teamwork/opengever.pdfconverter/>`_
is used, we require `Celery <http://www.celeryproject.org/>`_ and
`RabbitMQ <http://www.rabbitmq.com/>`_. In order to install RabbitMQ, you
first need to install `Erlang <http://www.erlang.org/>`_.


Sablon
^^^^^^

If ``opengever.meeting`` is activated (which it is for the default development
installation), the Ruby gem `Sablon <https://github.com/senny/sablon/>`_ is
required to generate documents from ``*.docx`` templates. Sablon is executed
as subprocess so the ``sablon`` script provided by the sablon gem must be
accessible as the user that is running gever instances.

In order for buildout to be able to install the `Sablon` gem, you need to
have `bundler` installed. For local development on Mac OS X it is recommended
to set up your Ruby using `rbenv <https://github.com/sstephenson/rbenv>`_
and the `ruby-build <https://github.com/sstephenson/ruby-build>`_ plugin:

.. code::

    git clone https://github.com/sstephenson/rbenv.git ~/.rbenv
    git clone https://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build
    echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bash_profile
    echo 'eval "$(rbenv init -)"' >> ~/.bash_profile
    source ~/.bash_profile
    rbenv install 2.1.5
    gem install bundler

The installation of the ``Sablon`` gem can then be performed by buildout (by
extending from `ruby-gems.cfg <https://raw.githubusercontent.com/4teamwork/gever-buildouts/master/ruby-gems.cfg>`_).


LDAP credentials
~~~~~~~~~~~~~~~~

LDAP and AD plugins get configured as usual, using an ``ldap_plugin.xml`` file
in the profile of the respective policy package - with one exception:

Credentials for the LDAP service (bind DN and bind password) will **NEVER** be
checked in in the ``ldap_plugin.xml``, but instead will be stored machine-wide
in a file ``~/.opengever/ldap/{hostname}.json`` where ``{hostname}`` refers to
the hostname of the LDAP server.

When an OpenGever client then is created using ``opengever.setup``, the
credentials are read from that file and configured for the LDAPUserFolder as
well as the active LDAP connection.

So, for a local development installation, create the following file:

.. code::

    ~/.opengever/ldap/ldap.4teamwork.ch.json

with these contents:

.. code::

    {
      "ldap":{
        "user":"<bind_dn>",
        "password":"<bind_pw>"
      }
    }


``<bind_dn>`` and ``<bind_pw>`` refer to the username and password for the
respective user in our development LDAP tree.


OGDS synchronization
--------------------

For quick lookups for user information and metadata (that isn't relevant for
security), we keep a mirrored list of users, groups, and group memberships in
SQL tables in the OGDS.

Among other things, this list of users is used to determine what users are
valid assignees for various objects: If a user was removed from the LDAP, he
is still supposed to be a valid assignee for existing objects, but should not
be suggested for selection for newly created objects.

Therefore users that are already contained in the SQL tables but have
disappeared from LDAP are not removed from SQL, but instead flagged as
``inactive`` upon synchroniszation.

There's several different ways to perform the OGDS synchronization:

- It can be triggered manually from the ``@@ogds-controlpanel`` (or by directly
  visiting the ``@@sync_users`` or ``@@sync_groups`` views)
- It will automatically be done when setting up a new AdminUnit
- It can be done from the shell by running the ``bin/instance sync_ogds``
  zopectl command (the respective instance must not be running)
- For deployments, a cron job that calls ``bin/instance0 sync_ogds`` should be
  created that syncs OGDS as needed

Since the OGDS is shared between AdminUnits in the same cluster, the
synchronization will only have to be performed on one Zope instance per
cluster.


Updating translations
---------------------

Updating translations can be done with the ``bin/i18n-build`` script.
It will scan the entire ``opengever.core`` package for translation files that
need updating, rebuild the respective ``.pot`` files and sync the ``.po`` files.

Alternatively it's also possible to only update a single subpackage, for example the ``dossier`` subpackage:

.. code::

    bin/i18n-build opengever.dossier


Updating the history file
-------------------------

The ``docs/HISTORY.txt`` file is a hotspot for git merge conflicts.
In order to reduce merge conflicts we use the git union merge strategy for
auto-resolving merge conflicts.
For this to work smoothly developmers must follow theese rules when adding
changelog entries:

1. Always add a new entry at the top of the ``unreleased`` section.
2. Add your ``[name]`` onto the *same line*, it should never be on a standalone
   line, otherwise it might be deleted by the union merge.
3. Do *not* insert any empty lines.
4. Awoid nested lists in your entry, because it makes auto-merging brittle.
   It is better to add each change as a separate changelog entry and prefix
   them, as shown below (see `Feature x`).
   If you must use nested lists, make sure to add an empty line before and
   after the list.
5. You *must rebase* when you do not "make the release", so that your entry is
   not added to an already released section. Git cannot resolve that.

Example:

.. code:: rst

    17.12.72 (unreleased)
    ---------------------

    - Fix critical bug. [Susanne]
    - Lots of changes after a lot of time. [Fritz]
    - Update translations. [Fritz]
    - Feature x: implement new things. [Susanne]
    - Feature x: fix bug. [Susanne]


Updating API docs
-----------------

In order to build the Sphinx API docs locally, use the provided
``bin/docs-build-api`` script:

.. code::

    bin/api-docs-build

This will build the docs (using the ``html`` target by default). If you'd like
to build a different output format, supply it as the fist argument to the
script (e.g. ``bin/docs-build-api latexpdf``).

If you made changes to any schema interfaces that need to make their way into
the docs, you need to run the ``bin/instance dump_schemas`` script before
running the ``docs-build-api`` script:

.. code::

    bin/instance dump_schemas

This will update the respective schema dumps in ``docs/schema-dumps/`` that
are then used by the ``docs-build-api`` script to render restructured text
schema docs.


Scripts
-------
Scripts are located in ``/scripts``.


**Repository configuration:**

`convert_csv_repository_to_xlsx.py <https://github.com/4teamwork/opengever.core/blob/master/scripts/convert_csv_repository_to_xlsx.py>`:
Converts repository configuration from old format (repository.csv) to new format (xlsx).


*You have to install openpyxl to run this script!*

.. code::

    bin/zopepy scripts/convert_csv_repository_to_xlsx.py <path to repository csv file> <path for new xlsx file>


Creating policies
-----------------
A script to semi-automatically create policies is provided as ``bin/create-policy``. The script runs in interactive mode and generates policies based on the questions asked. Policies are stored in the source directory ``src``.

Policy templates are avilable from the ``opengever.policytemplates`` package. At the time of writing there is only one policy template for simple SAAS policies.

Once a new policy has been generated the following things need to be added manually:

- an initial repository (as excel file)
- initial template files, if required
- initial sablon templates, if required
- Some more complex confiuration options like retention periods and multiple inboxes/template folders


Tests
-----

Parallelisation
~~~~~~~~~~~~~~~

Use ``bin/mtest`` for running all test in multiple processes. Alternatively ``bin/test`` runs the tests in sequence.
The multi process script distributes the packages (e.g. ``opengever.task``, ``opengever.base``, etc) into multiple processes,
trying to balance the amount of test suites, so that it speeds up the test run.

The ``bin/mtest`` script can be configured with environment variables:

- ``MTEST_PROCESSORS`` - The amount of processors used in parallel. It should be no greater than the amount
  of available CPU cores. Defaults to ``4``.
- ``MTEST_NOCOLORS`` - Set this to a positive value (``true``) for disabling the colorization of the output.
  The colorization is useful for the visual separation of the output of the various processes,
  but it is not useful in a environment without color support.

Builder API
~~~~~~~~~~~

This project uses the `ftw.builder <http://github.com/4teamwork/ftw.builder>`_ package based on the `Builder pattern <http://en.wikipedia.org/wiki/Builder_pattern>`_ to create test data.
The opengever specific builders are located in `opengever.testing <https://github.com/4teamwork/opengever.core/blob/master/opengever/testing/builders.py>`_

To use the `Builder API` you need to import the ``Builder`` function:

.. code:: python

     from ftw.builder import Builder
     from ftw.builder import create


Then you can use the ``Builder`` function in your test cases:

.. code:: python

     dossier = create(Builder("dossier"))
     task = create(Builder("task").within(dossier))
     document = create(Builder("document")
                       .within(dossier)
                       .attach_file_containing("test_data"))

Note that when using the ``OPENGEVER_FUNCTIONAL_TESTING`` Layer the ``Builder`` will automatically do a ``transaction.commit()`` when ``create()`` is called.


Testing Inbound Mail
--------------------

For easy testing of inbound mail (without actually going through an MTA) there's
a script ``bin/test-inbound-mail`` that can be used to test creation of inbound
mail:

``cat testmail.eml | bin/test-inbound-mail``

The script assumes you got an instance running on port ``${instance:http-address}``, a GEVER client called ``fd`` and an omelette with ``ftw.mail`` in it installed. It will then feed the mail from stdin to
the ``ftw.mail`` inbound view, like Postfix would.


Deployment
----------

The following section describes some aspects of deploying OneGov GEVER. If you need an example of a simple deployment profile have a look at the examplecontent profiles, see: https://github.com/4teamwork/opengever.core/tree/master/opengever/examplecontent.


Setup Wizard
~~~~~~~~~~~~

The manage_main view of the Zope app contains an additional button "Install OneGov GEVER" to add a new deployment. It leads to the setup wizard where a deployment profile and an LDAP configuration profile can be selected.

The setup wizard can be configured with the following environment variable:

- ``IS_DEVELOPMENT_MODE`` - If set pre-selects the following options in the setup wizard: Import of LDAP users, Development Mode and Purge SQL. Currently these are all available options.


Deployment Profiles
^^^^^^^^^^^^^^^^^^^

Deployment profiles can be selected in the setup wizard. They are used to link a Plone site with its corresponding ``AdminUnit`` and they usually include a policy profile, additional init profiles and further Plone-Site configuration options. Deployment profiles are configured in ZCML:

.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:opengever="http://namespaces.zope.org/opengever"
        i18n_domain="my.package">

        <opengever:registerDeployment
            title="Development with examplecontent"
            policy_profile="opengever.examplecontent:default"
            additional_profiles="opengever.setup:repository_root,
                                 opengever.setup:default_content,
                                 opengever.examplecontent:init"
            admin_unit_id="admin1"
            />

    </configure>

See https://github.com/4teamwork/opengever.core/blob/master/opengever/setup/meta.py for a list of all possible options.


LDAP Profiles
^^^^^^^^^^^^^

LDAP profiles can be selected in the setup wizard. They are used to install an LDAP configuration profile. LDAP profiles are configured in ZCML:

.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:opengever="http://namespaces.zope.org/opengever"
        i18n_domain="my.package">

        <opengever:registerLDAP
            title="4teamwork LDAP"
            ldap_profile="opengever.examplecontent:4teamwork-ldap"
            />

    </configure>

See https://github.com/4teamwork/opengever.core/blob/master/opengever/setup/meta.py for a list of all possible options.


Content creation
~~~~~~~~~~~~~~~~

Opengever defines four additional generic setup setuphandlers to create initial `AdminUnit` and `OrgUnit` OGDS entries, create initial  documents/document templates, configure local roles and create an initial repository. Of course ``ftw.inflator`` content creation is available as well, for details see https://github.com/4teamwork/ftw.inflator.


Creating initial AdminUnit/OrgUnit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add a ``unit_creation`` folder to your generic setup profile. To that folder add the files ``admin_units.json`` and/or ``org_units.json``. The content is created when the generic setup profile is applied. Note also that this content is created before ``ftw.inflator`` content and before all the other custom gever content creation handlers.


AdminUnit example:

.. code:: json

    [
      {
        "unit_id": "admin1",
        "title": "Admin Unit 1",
        "ip_address": "127.0.0.1",
        "site_url": "http://localhost:8080/admin1",
        "public_url": "http://localhost:8080/admin1",
        "abbreviation": "A1"
      }
    ]

OrgUnit example:

.. code:: json

  [
    {
      "unit_id": "org1",
      "title": "Org Unit 1",
      "admin_unit_id": "admin1",
      "users_group_id": "og_demo-ftw_users",
      "inbox_group_id": "og_demo-ftw_users"
    }
  ]


Creating initial repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gever repositories are initialized from an excel file. To add initial repository setup add a folder ``opengever_repositories`` to your generic setup profile. Each ``*.xlsx`` file in that folder will then be processed, the filename will serve as the ID for the repository root. See `ordnungssystem.xlsx <https://github.com/4teamwork/opengever.core/blob/master/opengever/examplecontent/profiles/repository_minimal/opengever_repositories/ordnungssystem.xlsx>`_ for an example. Note that this setuphandler is called after `ftw.inflator` but before custom GEVER content.


Creating GEVER specific content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Documents and Document templates are created with a customized ``ftw.inflator`` pipeline since they need special handling to have correct initial file versions. Thus documents should never be created with ``ftw.inflator`` but always with our customized pipeline. Since the custom pipeline is based on ``ftw.inflator`` we suggest to create all gever-content with this new pipeline.

To create content add an ``opengever_content`` folder to your generic setup profile. All JSON files in this folder are then processed similar to ``ftw.inflator``. Note that this setuphandler is called after `ftw.inflator`.


Configuring local roles
^^^^^^^^^^^^^^^^^^^^^^^

To decouple local role assignment from content creation opengever introduces a separate setuphandler to configure local roles. To configure local roles add a ``local_role_configuration`` folder to your generic setup profile. All JSON files in that folder are then processed. Note that this setuphandler is called after `ftw.inflator`.


Example configuration:

.. code:: json

  [
      {
          "_path": "ordnungssystem",
          "_ac_local_roles": {
              "og_demo-ftw_users": [
                  "Contributor",
                  "Editor",
                  "Reader"
              ]
          }
      }
  ]
