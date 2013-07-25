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

Updating translations
---------------------

Updating translations can be done with the ``bin/i18n-build`` script.
It will scan the entire ``opengever.core`` package for translation files that
need updating, rebuild the respective ``.pot`` files and sync the ``.po`` files.

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
