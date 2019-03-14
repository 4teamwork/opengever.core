from collections import OrderedDict
from ftw.mail.interfaces import IEmailAddress
from opengever.document.events import FileAttachedToEmailEvent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.events import DossierAttachedToEmailEvent
from opengever.officeconnector import _
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_restapi_feature_enabled
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from plone import api
from plone.protect import createToken
from plone.rest import Service
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.i18n import translate
import json


class OfficeConnectorURL(Service):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS."""

    def render(self):
        pass

    def create_officeconnector_url_json(self, payload):
        self.request.response.setHeader('Content-Type', 'application/json')

        url = create_oc_url(self.request, self.context, payload)

        if url:
            return json.dumps(dict(url=url))

        # Fail per default
        self.request.response.setStatus(500)

        message = _(
            u'error_oc_url_too_long',
            default=(
                u"Unfortunately it's not currently possible to attach this "
                u'many documents. Please try again with fewer documents '
                u'selected.'
                ),
            )

        return json.dumps(dict(
            error=dict(
                message=translate(
                    message,
                    context=self.request,
                    )
                )
            ))


class OfficeConnectorAttachURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'attach' action payload for this
    document.
    """

    def render(self):
        if is_officeconnector_attach_feature_enabled():
            payload = {'action': 'attach'}
            return self.create_officeconnector_url_json(payload)

        # Fail per default
        raise NotFound


class OfficeConnectorAttachAsPDFURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'attach' action payload for this
    document, but end up fetching the PDF representation instead.
    """

    def render(self):
        if is_officeconnector_attach_feature_enabled():
            payload = {'action': 'attach', 'as_pdf': True}
            return self.create_officeconnector_url_json(payload)

        # Fail per default
        raise NotFound


class OfficeConnectorCheckoutURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'checkout' action payload for
    this document.
    """

    def render(self):
        if is_officeconnector_checkout_feature_enabled():
            payload = {'action': 'checkout'}

            return self.create_officeconnector_url_json(payload)

        # Fail per default
        raise NotFound


class OfficeConnectorOneOffixxURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'oneoffixx' action payload for
    this document.
    """

    def render(self):
        if is_oneoffixx_feature_enabled():
            payload = {'action': 'oneoffixx'}

            return self.create_officeconnector_url_json(payload)

        # Fail per default
        raise NotFound


class OfficeConnectorPayload(Service):
    """Issue JSON instruction payloads for OfficeConnector."""

    def __init__(self, context, request):
        super(OfficeConnectorPayload, self).__init__(context, request)
        self.uuids = json.loads(request['BODY'])

    @staticmethod
    def document_is_valid(document):
        return document and (document.is_shadow_document() or document.has_file())

    def get_base_payloads(self):
        # Require an authenticated user
        if not api.user.is_anonymous():
            documents = OrderedDict()

            for uuid in self.uuids:
                document = api.content.get(UID=uuid)

                if self.document_is_valid(document):
                    documents[uuid] = document

        else:
            # Fail per default
            raise Forbidden

        if documents:
            payloads = []

            for uuid, document in documents.items():
                payloads.append(
                    {
                        'csrf-token': createToken(),
                        'document-url': document.absolute_url(),
                        'document': document,
                        'uuid': uuid,
                        }
                    )

            return payloads

        # Fail per default
        raise NotFound

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
        payloads = self.get_base_payloads()

        dossier_notifications = {}

        for payload in payloads:
            document = payload['document']
            parent_dossier = document.get_parent_dossier()

            if parent_dossier and IDossierMarker.providedBy(parent_dossier) and parent_dossier.is_open():
                payload['bcc'] = IEmailAddress(self.request).get_email_for_object(parent_dossier)

                parent_dossier_uuid = api.content.get_uuid(parent_dossier)

                if parent_dossier_uuid not in dossier_notifications:
                    dossier_notifications[parent_dossier_uuid] = []

                dossier_notifications[parent_dossier_uuid].append(document)

            payload['title'] = document.title_or_id()
            payload['content-type'] = document.get_file().contentType
            payload['download'] = document.get_download_view_name()
            payload['filename'] = document.get_filename()
            del payload['document']
            notify(FileAttachedToEmailEvent(document))

        for uuid, documents in dossier_notifications.iteritems():
            dossier = api.content.get(UID=uuid)
            notify(DossierAttachedToEmailEvent(dossier, documents))

        return json.dumps(payloads)


class OfficeConnectorCheckoutPayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Consists of the minimal instruction set with which to perform a full
    checkout checkin cycle for a file attached to a document.
    """

    def render(self):
        payloads = self.get_base_payloads()

        # Upload API will be included as a registry setting in the future when
        # the plone.api endpoint gets made - for now we've made a custom upload
        # form.
        for payload in payloads:
            # A permission check to verify the user is also able to upload
            document = payload.pop('document')
            authorized = api.user.has_permission('Modify portal content', obj=document)

            if authorized:
                if document.is_shadow_document():
                    # Oneoffixx is only used for .docx files in opengever.core
                    payload['content-type'] = IAnnotations(document)["content_type"]
                else:
                    payload['content-type'] = document.get_file().contentType

                payload['download'] = document.get_download_view_name()

                # for oneoffixx, we checkout the document to fall in the normal
                # checkout-checkin cycle.
                if document.is_shadow_document():
                    payload['filename'] = IAnnotations(document).get("filename")
                else:
                    payload['filename'] = document.get_filename()

                if is_officeconnector_restapi_feature_enabled():
                    reauth_querystring = '&'.join((
                        '_authenticator={}'.format(payload.pop('csrf-token')),
                        'mode=external',
                        'reauth=1',
                    ))
                    payload['reauth'] = '?'.join(('@@checkout_documents', reauth_querystring))
                    payload['status'] = 'status'
                    payload['lock'] = '@lock'
                    payload['checkout'] = '@checkout'
                    payload['upload'] = '@tus-replace'
                    payload['checkin'] = '@checkin'
                    payload['unlock'] = '@unlock'
                else:
                    payload['checkin-with-comment'] = '@@checkin_document'
                    payload['checkin-without-comment'] = 'checkin_without_comment'
                    payload['checkout'] = '@@checkout_documents'
                    payload['upload-form'] = 'file_upload'

            else:
                # Fail per default
                raise Forbidden

        self.request.response.setHeader('Content-type', 'application/json')

        return json.dumps(payloads)


class OfficeConnectorOneOffixxPayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Contains the instruction set to generate a document from a oneoffixx
    template (connect-xml), then checkout the corresponding document (checkout-url)
    to open the created document in an editor. From there the normal checkout,
    checkin cycle can begin.
    """

    @staticmethod
    def document_is_valid(document):
        return document and document.is_shadow_document()

    def render(self):
        payloads = self.get_base_payloads()

        for payload in payloads:
            # A permission check to verify the user is also able to upload
            authorized = api.user.has_permission(
                'Modify portal content',
                obj=payload['document'],
                )

            if authorized:
                document = payload['document']
                payload['filename'] = IAnnotations(document).get("filename")
                # Oneoffixx is only used for .docx files in opengever.core
                payload['content-type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                del payload['document']
                payload['connect-xml'] = '@@oneoffix_connect_xml'

            else:
                # Fail per default
                raise Forbidden

        self.request.response.setHeader('Content-type', 'application/json')

        return json.dumps(payloads)
