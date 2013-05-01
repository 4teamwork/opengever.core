Introduction
============


Copying related documents
-------------------------

When adding a response to a task which resolves the task, the user is
redirected to a wizard under certain circumstances for copying the related
documents to the inbox of one of his assigned clients.

The reason for this copying process is that users which work on foreign clients
have to be able to store the work they did on their own client for traceability
reasons.

The wizard is called when following conditions are met:

1. The user is assigned to at least one *other* client.
2. The user is member of the inbox group of at least one of the clients (1.)
3. The task type category is 'uni_val'

The user is able to decied to copy the documents or not. He can the select one
of the clients (of 1. and 2.) as target.

All documents which are either within the task or have a relation with the task
are copied to the inbox of the target client.

The inbox of the target client has to have the id "eingangskorb" and is located
on the root of the plone site.
