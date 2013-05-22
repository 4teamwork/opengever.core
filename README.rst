opengever.core
==============

Development installation
------------------------

To get a basic development installation running follow the steps below:

.. code::

    $ git clone ...
    $ ln -s development.cfg buildout.cfg
    $ python bootstrap.py
    $ bin/buildout

External dependencies
~~~~~~~~~~~~~~~~~~~~~

opengever.core requires a sql database to store some configuriation. Before you can configure your first client you need to set up the database.

.. code::

    $ brew install mysql
    $ mysql -u root
    > CREATE DATABASE opengever;
    > GRANT ALL ON opengever.* TO opengever@localhost IDENTIFIED BY 'opengever';

Tests
-----

Use ``bin/test`` to execute all the tests in this package.

Builder API
~~~~~~~~~~~

This project uses the `Builder pattern <http://en.wikipedia.org/wiki/Builder_pattern>`_ to create test data.
The implementation is located in `opengever.testing <https://github.com/4teamwork/opengever.core/blob/master/opengever/testing/builders.py>`_

To use the `Builder API` you need to import the `Builder` function:

.. code:: python

     from opengever.testing import Builder


Then you can use the `Builder` function in your test cases:

.. code:: python

     dossier = Builder("dossier").create()
     task = Builder("task").within(dossier).create()
     document = Builder("document") \
         .within(dossier) \
         .attach_file_containing("test_data") \
         .create()
         
Note that `Builder` will automatically do a `transaction.commit()` when `create()` is called.
You can disable this feature on a per test-case basis on the `BuilderSession`
     
