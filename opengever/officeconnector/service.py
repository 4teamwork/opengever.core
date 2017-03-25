from ftw.mail.interfaces import IEmailAddress
from opengever.document.events import FileAttachedToEmailEvent
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from plone import api
from plone.protect import createToken
from plone.rest import Service
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.event import notify
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import json


class OfficeConnectorURL(Service):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS."""

    def create_officeconnector_url_json(self, payload):
        self.request.response.setHeader('Content-type', 'application/json')

        url = create_oc_url(self.request, self.context, payload)

        if url:
            return json.dumps(dict(url=url))
        else:
            self.request.response.setStatus(500)
            return json.dumps(dict(error=dict(
                type='Generated URL too long',
                message='The URL is too long for IE11',
            )))


class OfficeConnectorAttachURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'attach' action payload for this
    document.
    """

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_attach_feature_enabled():
            raise NotFound
        payload = {'action': 'attach'}
        return self.create_officeconnector_url_json(payload)


class OfficeConnectorCheckoutURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'checkout' action payload for
    this document.
    """

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_checkout_feature_enabled():
            raise NotFound

        payload = {'action': 'checkout'}

        return self.create_officeconnector_url_json(payload)


class OfficeConnectorPayload(Service):
    """Issue JSON instruction payloads for OfficeConnector."""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(OfficeConnectorPayload, self).__init__(context, request)
        self.uuid = None
        self.document = None

    def publishTraverse(self, request, name):
        # This gets called once per path segment
        if self.uuid is None:
            self.uuid = name
        else:
            # Block traversing further path segments
            raise NotFound(self, name, request)
        return self

    def get_base_payload(self):
        # Do not 404 if we do not have a normal user
        if api.user.is_anonymous():
            raise Forbidden
        self.document = api.content.get(UID=self.uuid)
        if not self.document or not self.document.file:
            raise NotFound
        return {
            'content-type': self.document.file.contentType,
            'csrf-token': createToken(),
            'document-url': self.document.absolute_url(),
            'download': 'download',
            'filename': self.document.get_filename(),
            }

    def render(self):
        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(self.get_base_payload())


class OfficeConnectorAttachPayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Consists of the minimal instruction set with which to perform an attach to
    email action.
    """

    def render(self):
        self.request.response.setHeader('Content-type', 'application/json')

        payload = self.get_base_payload()

        parent_dossier = self.document.get_parent_dossier()
        if parent_dossier and parent_dossier.is_open():
            payload['bcc'] = IEmailAddress(
                self.request).get_email_for_object(parent_dossier)

        notify(FileAttachedToEmailEvent(self.document))

        return json.dumps(payload)


class OfficeConnectorCheckoutPayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Consists of the minimal instruction set with which to perform a full
    checkout checkin cycle for a file attached to a document.
    """

    def render(self):
        payload = self.get_base_payload()

        # A permission check to verify the user is also able to upload
        if not api.user.has_permission('Modify portal content',
                                       obj=self.document):
            raise Forbidden

        # Upload API will be included as a registry setting in the future when
        # the plone.api endpoint gets made - for now we've made a custom upload
        # form.
        payload['checkin-with-comment'] = '@@checkin_document'
        payload['checkin-without-comment'] = 'checkin_without_comment'
        payload['checkout'] = '@@checkout_documents'
        payload['upload-form'] = 'file_upload'
        payload['upload-api'] = None

        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(payload)
