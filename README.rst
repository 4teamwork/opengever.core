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

For production deployments, this module will be installed by Ops via Puppet
(it's now packaged as an RPM).

If you need this module for local development on macOS, you can also install
it using Perl ``local::lib`` and CPAN. You then need to install Perl,
``perl-YAML`` and the following Perl modules:

.. code::

    Email::Outlook::Message
    Email::LocalDelivery
    Getopt::Long
    Pod::Usage

In the end, GEVER will look for the ``msgconvert`` executable in ``$PATH``.


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
    rbenv install 2.3.3
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


Installing and activating Solr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the Solr configuration in your `buildout.cfg` and add the Solr directive:

.. code::

    [buildout]
    extends =
        development.cfg
        https://raw.githubusercontent.com/4teamwork/gever-buildouts/master/solr.cfg
    solr-port = 8983

    [solr]
    url = http://archive.apache.org/dist/lucene/solr/7.3.0/solr-7.3.0.tgz
    md5sum = dfb6893fc656e14919df48ff654d38f2


Buildout

.. code::

    $ bin/buildout

Then start Solr

.. code::

    $ bin/solr start

Run the `activate_solr` maintenance script:

.. code::

    $ bin/instance run src/opengever.maintenance/opengever/maintenance/scripts/activate_solr.py


Setting up a multi-admin environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need a multi-admin environment, make sure the basic development dependencies above are satisfied and run the following steps:

Pleace note that the default database-name for multi-admin environment is ``opengever-multi-admin``

.. code::

    $ git clone git@github.com:4teamwork/opengever.core.git
    $ cd opengever.core
    $ ln -s development-multi-admin.cfg buildout.cfg
    $ python bootstrap.py
    $ bin/buildout
    $ bin/instance fg

Go to ``http://localhost:8080/manage_main`` and click on ``Install OneGov GEVER``,

For the first admin-unit choose the following settings:

+----------------------------------+------------------------------------------+
| Property                         | Value                                    |
+==================================+==========================================+
| Deployment profile               | Choose the **Finanzdirektion (FD) (DEV)**|
+----------------------------------+------------------------------------------+
| LDAP configuration profile       | OneGovGEVER-Demo LDAP                    |
+----------------------------------+------------------------------------------+
| Import users from LDAP into OGDS | **True**                                 |
+----------------------------------+------------------------------------------+
| Development mode                 | False                                    |
+----------------------------------+------------------------------------------+
| Purge SQL                        | **True**                                 |
+----------------------------------+------------------------------------------+

For the second admin-unit choose the following settings:

+----------------------------------+--------------------------------------+
| Property                         | Value                                |
+==================================+======================================+
| Deployment profile               | Choose the **Ratskanzlei (RK) (DEV)**|
+----------------------------------+--------------------------------------+
| LDAP configuration profile       | OneGovGEVER-Demo LDAP                |
+----------------------------------+--------------------------------------+
| Import users from LDAP into OGDS | **False**                            |
+----------------------------------+--------------------------------------+
| Development mode                 | False                                |
+----------------------------------+--------------------------------------+
| Purge SQL                        | **False**                            |
+----------------------------------+--------------------------------------+

After installing both admin-units, you have to set a shared session-secret to share login-sessions between admin-units. To do this, do the following steps for both admin-units:

- Goto: ``{admin-unit}/acl_users/session/manage_secret``
- Set a ``Shared secret``

Lastly you have to change the admin-unit urls in the database to localhost.

- Table: ``admin_units``
- Properties: ``site_url`` and ``public_url``

PostgreSQL-Example:

.. code:: postgresql

    UPDATE admin_units SET site_url = replace("site_url", 'https://dev.onegovgever.ch', 'http://localhost:8080'), public_url = replace("public_url", 'https://dev.onegovgever.ch', 'http://localhost:8080');


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

Usually you work on a specific package and you want to only rebuild this package:

.. code::

    bin/i18n-build opengever.dossier

For building all packages, use the ``--all`` option:

.. code::

    bin/i18n-build --all


Theme Development
-----------------

You will need the ``sass`` command for compiling ``SCSS`` to ``CSS``. Start the
``bin/sass-watcher`` script and it will pick up changes base on filesystem
events and compile the style files automatically for you.

There is a ``Gemfile`` to help make ``SASS`` versions consistent across
development environments. Please refer to http://bundler.io/ for more details.


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
4. Avoid nested lists in your entry, because it makes auto-merging brittle.
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
``bin/docs-build-public`` script:

.. code::

    bin/api-docs-build

This will build the docs (using the ``html`` target by default). If you'd like
to build a different output format, supply it as the fist argument to the
script (e.g. ``bin/docs-build-public latexpdf``).

If you made changes to any schema interfaces that need to make their way into
the docs, you need to run the ``bin/instance dump_schemas`` script before
running the ``docs-build-public`` script:

.. code::

    bin/instance dump_schemas

This will update the respective schema dumps in ``docs/schema-dumps/`` that
are then used by the ``docs-build-public`` script to render restructured text
schema docs.


Versions
--------

Versions are pinned in the file ``versions.cfg`` in the ``opengever.core``
package.

Versions in development
~~~~~~~~~~~~~~~~~~~~~~~

In order to add a new dependency or to update one or many dependencies,
follow these steps:

1. Append new and changed version pinnings at the end of the ``[versions]``
   section in the ``versions.cfg`` in your local ``opengever.core`` checkout.
2. Run ``bin/cleanup-versions-cfg``, review and confirm the changes.
   This script removes duplicates and sorts the dependencies.
3. Commit the changes to your branch and submit it along with other changes as
   pull request.


Versions in producion
~~~~~~~~~~~~~~~~~~~~~

For production deployments, the ``versions.cfg`` of a tag can be included
with a raw github url in buildout like this:

.. code:: ini

    [buildout]
    extends =
        https://raw.githubusercontent.com/4teamwork/opengever.core/2017.4.0/versions.cfg



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

Fixture Objects
~~~~~~~~~~~~~~~

The fixture objects can be accessed on test-classes subclassing
``IntegrationTestCase`` with attribute access (``self.dossier``).

Users
^^^^^

.. <fixture:users>

- ``self.administrator``: ``nicole.kohler``
- ``self.committee_responsible``: ``franzi.muller``
- ``self.dossier_manager``: ``faivel.fruhling``
- ``self.dossier_responsible``: ``robert.ziegler``
- ``self.manager``: ``admin``
- ``self.meeting_user``: ``herbert.jager``
- ``self.member_admin``: ``david.meier``
- ``self.records_manager``: ``ramon.flucht``
- ``self.regular_user``: ``kathi.barfuss``
- ``self.secretariat_user``: ``jurgen.konig``
- ``self.workspace_admin``: ``fridolin.hugentobler``
- ``self.workspace_guest``: ``hans.peter``
- ``self.workspace_member``: ``beatrice.schrodinger``
- ``self.workspace_owner``: ``gunther.frohlich``

.. </fixture:users>

Objects
^^^^^^^

.. <fixture:objects>

.. code::

  - self.committee_container
    - self.committee
      - self.cancelled_meeting
      - self.decided_meeting
      - self.decided_proposal
      - self.meeting
      - self.submitted_proposal
      - self.submitted_word_proposal
    - self.committee_participant_1
    - self.committee_participant_2
    - self.committee_president
    - self.empty_committee
    - self.inactive_committee_participant
  - self.contactfolder
    - self.franz_meier
    - self.hanspeter_duerr
  - self.inbox
    - self.inbox_document
    - self.inbox_forwarding
      - self.inbox_forwarding_document
  - self.private_root
    - self.private_folder
      - self.private_dossier
        - self.private_document
        - self.private_mail
  - self.repository_root
    - self.branch_repofolder
      - self.leaf_repofolder
        - self.cancelled_meeting_dossier
        - self.closed_meeting_dossier
        - self.decided_meeting_dossier
        - self.dossier
          - self.document
          - self.draft_proposal
          - self.draft_word_proposal
          - self.empty_document
          - self.mail_eml
          - self.mail_msg
          - self.proposal
            - self.proposaldocument
          - self.sequential_task
            - self.seq_subtask_1
            - self.seq_subtask_2
            - self.seq_subtask_3
          - self.subdossier
            - self.subdocument
            - self.subsubdossier
          - self.subdossier2
          - self.task
            - self.subtask
            - self.taskdocument
          - self.word_proposal
        - self.empty_dossier
        - self.expired_dossier
          - self.expired_document
          - self.expired_task
        - self.inactive_dossier
          - self.inactive_document
          - self.inactive_task
        - self.meeting_dossier
          - self.meeting_document
          - self.meeting_task
            - self.meeting_subtask
    - self.empty_repofolder
  - self.templates
    - self.ad_hoc_agenda_item_template
    - self.asset_template
    - self.docprops_template
    - self.dossiertemplate
      - self.subdossiertemplate
    - self.empty_template
    - self.meeting_template
      - self.paragraph_template
    - self.normal_template
    - self.proposal_template
    - self.recurring_agenda_item_template
    - self.sablon_template
    - self.subtemplates
      - self.subtemplate
    - self.tasktemplatefolder
      - self.tasktemplate
  - self.workspace_root
    - self.workspace
      - self.workspace_folder

.. </fixture:objects>

Other values
^^^^^^^^^^^^

.. <fixture:raw>

- ``self.committee_id``: ``1``
- ``self.empty_committee_id``: ``2``

.. </fixture:raw>



Parallelisation
~~~~~~~~~~~~~~~

Use ``bin/mtest`` for running all test in multiple processes. Alternatively ``bin/test`` runs the tests in sequence.
The multi process script distributes the packages (e.g. ``opengever.task``, ``opengever.base``, etc) into multiple processes,
trying to balance the amount of test suites, so that it speeds up the test run.

The ``bin/mtest`` script can be configured with environment variables:

- ``MTEST_PROCESSORS`` - The amount of processors used in parallel. It should be no greater than the amount
  of available CPU cores. Defaults to ``4``.

Functional or integration testing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are shifting the tests from the older functional testing layer to the newer
integration testing layer.

**Integration testing:**

- Should be used for new tests!
- Comes with a preinstalled `testing fixtures`_.
- Transactions are disabled for isolation purposes: `transaction.commit` is not allowed in tests.
- Uses ``ftw.testbrowser``'s ``TraversalDriver``.

**Functional testing:**

- Should *not be used* for new tests, when possible.
- Is factory-based, using ``ftw.builder``.
- Uses transactions.
- Limited / slow database isolation: a fresh setup is necessary for each test.


Example integration test with browser:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   from ftw.testbrowser import browsing
   from ftw.testbrowser.pages import statusmessages
   from opengever.testing import IntegrationTestCase

   class TestExampleView(IntegrationTestCase):

       @browsing
       def test_example_view(self, browser):
           self.login(self.dossier_responsible, browser)
           browser.open(self.dossier, view='example_view')
           statusmessages.assert_no_error_messages()


Best practices
~~~~~~~~~~~~~~

These best practices apply to the new **integration testing** layer.

Do not commit the transaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Committing the transaction will break isolation.
The testing layer will prevent you from interacting with the transaction.

Use the fixture objects
^^^^^^^^^^^^^^^^^^^^^^^

The `testing fixtures`_ create content objects, users, groups and client
configurations (admin units, org units) which are available for all tests.
They can and should be modified to the needs of the test.

Avoid creating objects (with ``ftw.builder``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating objects with ``ftw.builder`` or with ``ftw.testbrowser`` is expensive
because it takes a moment to index the object.
Therefore we want to avoid creating unnecessary objects within the tests
so that the tests are faster overall.

Tests which have the job to test object creation (e.g. through the browser)
obviously need to actually create an object, all other tests should try to
reuse objects from the fixture and modify them as needed.

Use users from fixture
^^^^^^^^^^^^^^^^^^^^^^

The fixture provides a set of standard users which should be used in tests.
Do not use ``plone.app.testing``'s test user with global roles as it does
not reflect properly how the security model of GEVER works.
In order to test features which can only be executed by the system or by a
``Manager``-user, the ``plone.app.testing``'s site owner may be used.

Login
^^^^^

Integration tests start with *no user logged in*.
The first thing each test should do, is to log in the user with the fewest
privileges required for doing the task under test.

The login command should *not* be moved to the ``setUp`` method; it should be
clearly visible at the beginning of each test, so that a reader has the necessary
context without scrolling to the top of the file.

When authenticated preparations are required in the ``setUp`` method, use
``self.login`` as a context manager in order to cleanup the authentication
on exit, so that the tests still start anonymously.

.. code:: python

   from opengever.testing import IntegrationTestCase
   from ftw.testbrowser import browsing

   class TestExampleView(IntegrationTestCase):

       def setUp(self):
           super(TestExampleView, self).setUp()
           with self.login(self.administrator):
               self.dossier.prepare_for_test()

       def test_server_side(self):
           self.login(self.dossier_responsible)
           self.assertTrue(self.dossier.can_do_important_things())

       @browsing
       def test_client_side_with_browser(self, browser):
           self.login(self.regular_user, browser)
           browser.open(self.dossier)
           browser.click_on('Do important things')



Do not assert ``browser.contents``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The statement `self.assertIn('The label', browser.contents)` will print the
complete HTML document as failure message.
This is distracting and not useful at all.

Instead you should select specific nodes and do assertions on those nodes, e.g.

.. code:: python

   from opengever.testing import IntegrationTestCase
   from ftw.testbrowser import browsing

   class TestExampleView(IntegrationTestCase):

       @browsing
       def test_label(self, browser):
           self.assertEquals('The label',
                             browser.css('label.foo').first.text)

This allows the browser to help when print a nice error message when the node
was not found:
``NoElementFound: Empty result set: browser.css("label.foo") did not match any nodes.``

When the view does not return a complete HTML document but, for example, a status
only (``OK``), or it is some kind of API endpoint, ``browser.contents`` may be
asserted.


Use ``tearDown`` carefully
^^^^^^^^^^^^^^^^^^^^^^^^^^

Do not tear down changes which are taken care of by some kind of isolation:

- Do *not* tear down ZODB changes: the ZODB is isolated by ``plone.app.testing``.
- Do *not* tear down SQL changes: we take care of that in the SQL testing layer
  with savepoints / rollbacks.
- Do *not* tear down component registry changes (e.g. new adapters, utilities,
  event handlers) as this is taken care of by the
  `COMPONENT_REGISTRY_ISOLATION`_ layer.
- *Do* tear down modifications in environment variables (``os.environ``).
- *Do* tear down modifications stored in module globals (e.g.
  transmogrifier sections).

Use guard assertions
^^^^^^^^^^^^^^^^^^^^

When your test expects a specific state in order to work properly, this state
should be ensured by using guard assertions.

.. code:: python

    def test_closing_dossier(self):
        self.assertTrue(self.dossier.is_open(),
                        'Precondition: assumed dossier to be open')
        self.dossier.close()
        self.assertFalse(self.dossier.is_open())

If the ``self.dossier`` is changed to be not open by default anymore, the failure
should tell us that a precondition was no longer met rather than implying that
the ``close()`` method is broken.
The statement also acts as "given"-statement and a reader can easily figure out
what the precondition is, because it is visually separated.

Alternatively a precondition can be ensured by setting the state of the object:

.. code:: python

    def test_title_is_journalized_on_action(self):
        self.dossier.title = u'The dossier'
        action(self.dossier)
        self.assertEquals(u'The dossier',
                          last_journal_entry(self.dossier).title)

Activating feature flags
^^^^^^^^^^^^^^^^^^^^^^^^

Feature flags can by activated test-case-wide by setting a tuple of all
required flags:

.. code:: python

    class TestDossierTemplate(IntegrationTestCase):
        features = ('dossiertemplate',)

When a feature should not be activated test-case-wide it can be activated
within a single test:

.. code:: python

    class TestTemplates(IntegrationTestCase):

        def test_adding_dossier_template(self):
            self.activate_feature('meeting')


See the `list of feature flags <https://github.com/4teamwork/opengever.core/blob/master/opengever/testing/integration_test_case.py>`_.


Cache integration testing setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When developing ``opengever.core``, a developer often runs a single test module,
with ``bin/test -m opengever.dossier.tests.test_activate`` for instance.
This will set up a complete fixture each time.
In order to speed up the feedback loop when developing,
we try to cache the database after setting up the fixture.
This will speed up the test runs, but it also makes the result inaccurate:
if the cachekeys do not detect a relevant change, we may not realize
that something breaks.

Because the results are not accurate and this is an experiment, the feature is
considered experimental and therefore disabled by default.

You can enable the feature by setting an environment variable:

.. code:: sh

    GEVER_CACHE_TEST_DB=true bin/test -m opengever.dossier.tests.test_activate

There is also a binary which does that for you for just one run for convenience:

.. code:: sh

    bin/test-cached -m opengever.dossier.tests.test_activate

You can manually remove / rebuild the caches:

.. code:: sh

    ./bin/remove-test-cache

This feature is disabled on the CI server.

When the environment variable ``GEVER_CACHE_VERBOSE`` is set to ``true``,
a list of modified files will be printed whenever a cachekey is invalidated.
This can be useful to debug problems with the fixture cache:

.. code:: sh

    GEVER_CACHE_VERBOSE=true bin/test-cached -m opengever.dossier.tests.test_activate


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


Unit testing and mock tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~

opengever.core has some unit tests (without a testing layer) and some mock test cases (usually
with the ``COMPONENT_UNIT_TESTING`` testing layer).

When writing unit tests (with no layer), the developer must take into account that there is no
isolation at all. The developer must make sure that neither the test nor any component used
in the test leaks, or isolation must be ensured manually.
The developer should also take into account that components under tests (or their dependencies)
may be changed in the future.

By leaking we mean any kind of thing changed outside of the test scope. This includes registering
components (adapters, utilites), changing globals (``setSite``, registering transmogrifier
blueprints, environment variables) or any other action that can influence other components later.

If a developer cannot guarantee that the test is not leaking he/she shall not write a unit test,
but use at least the ``COMPONENT_UNIT_TESTING`` layer or write an integration test.

The ``COMPONENT_UNIT_TESTING`` provides a minimal isolation of z3 componentes (adapters,
utilites) and registers basic adapters such as annotations.

When using mock tests cases, which discourage from in general, always import the
``MockTestCase`` from ``ftw.testing`` in order to be compatible with ``COMPONENT_UNIT_TESTING``.


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


.. _testing fixtures: https://github.com/4teamwork/opengever.core/blob/master/opengever/testing/fixtures.py
.. _COMPONENT_REGISTRY_ISOLATION: https://github.com/4teamwork/ftw.testing#component-registry-isolation-layer
