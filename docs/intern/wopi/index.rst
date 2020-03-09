WOPI
====

WOPI_ (Web Application Open Platform Interface) is a protocol from Microsoft
that defines a set of operations that enables a client to access and change files
stored by a server. This allows the client to render files and provide file editing
functionality for files stored by the server.

.. _WOPI: https://docs.microsoft.com/en-us/openspecs/office_protocols/ms-wopi/0f0bf842-6353-49ed-91c0-c9d672f21200

WOPI is used to |intergrate Office Online|_ (formerly Office Web Apps) with OneGov GEVER.
For this purpose OGG needs to implement the WOPI protocol.

.. _intergrate Office Online: https://wopi.readthedocs.io/en/latest/
.. |intergrate Office Online| replace:: intergrate Office Online


Implementation
--------------

OGG implements a subset of the REST endpoints defined in the WOPI protocol which
are required to support editing documents using Office Online.

The following operations are implemented:

- CheckFileInfo_
- GetFile_
- PutFile_
- PutRelativeFile_
- Lock_
- GetLock_
- Unlock_
- UnlockAndRelock_
- RefreshLock_

.. _CheckFileInfo: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/CheckFileInfo.html
.. _GetFile: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/GetFile.html
.. _PutFile: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/PutFile.html
.. _PutRelativeFile: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/PutRelativeFile.html
.. _Lock: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/Lock.html
.. _GetLock: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/GetLock.html
.. _Unlock: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/Unlock.html
.. _UnlockAndRelock: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/UnlockAndRelock.html
.. _RefreshLock: https://wopi.readthedocs.io/projects/wopirest/en/latest/files/RefreshLock.html

Operations that are required to create, enumerate, rename or delete documents and
any container operations are currently not implemented.

The WOPI REST endpoints are provided under the path ``/wopi``.
Additionally there's a browser view (``office_online_edit`` for documents that
provides the Office Online IFrame. This view is visited by users when they open
or edit Office documents in Office Online.


Deployment
----------

To enable Office Online support in OGG the WOPI discovery URL
(``IWOPISettings.discovery_url``) needs to be configured
and the feature must be enabled (``IWOPISettings.enabled``)
in the registry.

On-Premise
~~~~~~~~~~

On-Premise installations require an |Office Online Server|_.
This server must be accessible by OGG and the users web browser over HTTPS. The
server must also be able to access OGG over HTTPS.

.. _Office Online Server: https://docs.microsoft.com/en-us/officeonlineserver/deploy-office-online-server
.. |Office Online Server| replace:: Office Online Server

Usually the discovery URL consists of the hostname of the Office Online Server and
the path /hosting/discovery.

Example discovery URL: https://officeonline.4teamwork.ch/hosting/discovery

SaaS
~~~~

For SaaS offerings, licensing prohibits the use of an on-premise Office Online Server.
Thus Office 365 must be used. Integration with Office 365 requires membership of
the Office 365 - Cloud Storage Partner Program.
Further domains must be white listed by Microsoft. For production Microsoft requires
a WOPI-dedicated subdomain (e.g. wopi.onegovgever.ch). This has not yet been setup.
Currently the WOPI endpoints are served over the application's domain.

Development
-----------

Running the Office Online integration locally is difficult because OGG needs
to be accessible by the Office Online Server.

The simplest way to test and develop the WOPI implementation is to use Microsoft's
|WOPI validator|_ tool.

.. _WOPI validator: https://github.com/Microsoft/wopi-validator-core
.. |WOPI validator| replace:: WOPI validator

There's a test that runs the WOPI validator tests. It requires docker and with
Docker Desktop (macOS) the ZServer needs to listen on all interfaces to be
accessible from the Docker container. This can be acomplished by setting the
environment variable ZSERVER_HOST before executing the test.

.. code-block::

  export ZSERVER_HOST="0.0.0.0"
  bin/test -m opengever.wopi -t test_validator

The WOPI validator can also be run manually against a running OGG instance.
This may be more convenient during development and allows to run just specific tests.
For this purpose a document with the extension .wopitest must be created.
After that the ``WOPISrc`` URL and the ``access token`` have to be extracted from the
``office_online_edit`` browser view and provided to the WOPI validator.

Example: run the ``PutFileReturnsDifferentVersion`` test

.. code-block::

  docker run -it --rm tylerbutler/wopi-validator -- \
    -w <WOPISrc> -t <access_token> -l 0 -s -n files.PutFileReturnsDifferentVersion

For testing with Microsoft's |testing environment|_ the domains `lab.onegovgever.ch`
and `dev.onegovgever.ch` have been registered.

.. _testing environment: https://wopi.readthedocs.io/en/latest/build_test_ship/environments.html#test-environment
.. |testing environment| replace:: testing environment

