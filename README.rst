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
