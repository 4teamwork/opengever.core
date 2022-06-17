.. _attendees_presence_states:

Anwesenheitsstatus von Meeting-Teilnehmern bearbeiten
=====================================================

Mit dem ``@attendees-presence-states`` Endpoint kann der Anwesenheitsstatus von Meeting-Teilnehmern bearbeitet werden. Es stehen drei verschiedene Status zur Verfügung: ``present``, ``excused`` und ``absent``.

**Beispiel-Request**:

  .. sourcecode:: http

    PATCH /workspaces/workspace-1/workspace-meeting-1/@attendees-presences-states HTTP/1.1
    Accept: application/json

    {
      "kathi.barfuss": "excused",
      "robert.ziegler": "absent",
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
