opengever.core
==============

Development installation
------------------------

To get a basic development installation running follow the steps below:

.. code::

    $ git clone git@github.com:4teamwork/opengever.core.git
    $ cd opengever.core
    $ ln -s development.cfg buildout.cfg
    $ python bootstrap.py
    $ bin/buildout

External dependencies
~~~~~~~~~~~~~~~~~~~~~

``opengever.core`` requires a SQL database to store some configuration. Before you can configure your first client you need to set up the database.

.. code::

    $ brew install mysql
    $ mysql -u root
    > CREATE DATABASE opengever;
    > GRANT ALL ON opengever.* TO opengever@localhost IDENTIFIED BY 'opengever';


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


Updating translations
---------------------

Updating translations can be done with the ``bin/i18n-build`` script.
It will scan the entire ``opengever.core`` package for translation files that
need updating, rebuild the respective ``.pot`` files and sync the ``.po`` files.

Alternatively it's also possible to only update a single subpackage, for example the ``dossier`` subpackage:

.. code::

    bin/i18n-build opengever.dossier

Scripts
-------
Scripts are located in ``/scripts``.


**Repository configuration:**

`convert_csv_repository_to_xlsx.py <https://github.com/4teamwork/opengever.core/blob/master/scripts/convert_csv_repository_to_xlsx.py>`:
Converts repository configuration from old format (repository.csv) to new format (xlsx).


*You have to install openpyxl to run this script!*

.. code::

    bin/zopepy scripts/convert_csv_repository_to_xlsx.py <path to repository csv file> <path for new xlsx file>



Tests
-----

Use ``bin/test`` to execute all the tests in this package.

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


Browser API
~~~~~~~~~~~

The center of the `Browser API` is the ``OGBrowser`` class. It's a
simple subclass of ``plone.testing.z2.Browser`` and the easiest way to
use it is to extend ``opengever.testing.FunctionalTestCase``:

.. code:: python

    from opengever.testing import FunctionalTestCase


    class TestExample(FunctionalTestCase):
        use_browser = True

        def test_first_example(self):
          self.browser # => instance of OGBrowser

Now you can use the ``self.browser`` instance:

.. code:: python

    self.browser.fill({'Title': "My first Dossier",
                       'Description': "This is my first Dossier"})
    self.browser.click('Save')
    self.browser.assert_url("http://nohost/plone/dossier-1")

Have a look at the `opengever.testing.browser module
<https://github.com/4teamwork/opengever.core/blob/master/opengever/testing/browser.py>`_
to see the complete API.
