Oneoffixx
=========

Oneoffixx_ is a |microsoft-office|_ template management solution from Sevitec_.
It needs its own client, but the ``opengever.core`` integration relies on
|office-connector|_ also being installed.

It can use |content-controls|_ for injecting values into the documents.

.. _microsoft-office: https://www.office.com/
.. |microsoft-office| replace:: Microsoft Office

.. _Oneoffixx: https://oneoffixx.com/en/
.. _Sevitec: https://www.sevitec.ch/

.. _office-connector: https://www.4teamwork.ch/loesungen/office-connector/
.. |office-connector| replace:: Office Connector

.. _content-controls: https://docs.microsoft.com/en-us/visualstudio/vsto/content-controls
.. |content-controls| replace:: content controls

Architecture
------------

The system, as we use it, has 6 moving parts which concern us.

Oneoffixx backend
^^^^^^^^^^^^^^^^^

From the point of view of the Oneoffixx backend, both OpenGEVER and Office
Connector are LOB-Apps.

.. image:: ../_static/img/oneoffixx-system-overview-onpremise.png

We need to have whitelisted Office Connector in the backend as a callback
target for the InvokeProcess_ mechanism.

.. _InvokeProcess: https://docs.oneoffixx.com/connect/de/connect-commands/#invokeprocess

We also need to have created a backend to backend account for the OpenGEVER
installation. This means we will have a client id, client secret and a
preshared key we need to use in order to authenticate_ to the backend in order
to obtain a per user impersonation grant ``urn:oneoffixx:oauth2:impersonate``.
