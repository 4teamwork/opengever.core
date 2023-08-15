from collections import OrderedDict
from opengever.document.events import FileAttachedToEmailEvent
from opengever.dossier.events import DossierAttachedToEmailEvent
from opengever.officeconnector import _
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import group_payloads_by_parent
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.officeconnector.helpers import parse_document_uids
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.workspace import is_workspace_feature_enabled
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


class OfficeConnectorCheckoutURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'checkout' action payload for
    this document.
    """

    def render(self):
        if self.context.is_collaborative_checkout():
            # Documents currently being edited in Office Online must not be
            # edited in Office Connector, even if checked out by the same user
            raise Forbidden

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
                        'version': document.get_current_version_id(),
                    }
                )

            return payloads

        # Fail per default
        raise NotFound

    def render(self):
        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(self.get_base_payload())


class OfficeConnectorAttachIsMailFileable(OfficeConnectorPayload):
    """Check if copy of mail with attachments can be filed in dossier.

    Returns True if the document selection allows for a copy of the
    mail to be filed, and False otherwise.

    Reasons for why the mail can't be filed could be because the containing
    dossier is in a closed state, or the document selection is spread across
    multiple dossiers, etc.

    This determination is made by using the same strategy to find valid
    parent containers as the OfficeConnectorAttachPayload endpoint below.

    This is not a regular OfficeConnectorPayload view. It's not getting called
    by OC, but the gever-ui instead. It expects a {"documents": list_of_paths}
    mapping in the request body, same as the OfficeConnectorURL endpoints.
    It then resolves those paths to UUIDs, and only then starts using
    functionality from OfficeConnectorPayload to process them as payloads.
    """

    def __init__(self, context, request):
        super(OfficeConnectorAttachIsMailFileable, self).__init__(context, request)
        self.uuids = []

    def render(self):
        self.request.response.setHeader('Content-type', 'application/json')

        self.uuids = parse_document_uids(self.request, self.context, action='attach')
        if not self.uuids:
            raise NotFound

        payloads = self.get_base_payloads()
        group_payloads_by_parent(payloads, self.request)

        # This mirrors the logic that OC does on the client side: Only add
        # BCC if there's exactly one unique BCC address across payloads.
        bcc_addresses = {payload.get('bcc') for payload in payloads}
        if len(bcc_addresses) == 1 and bcc_addresses.pop():
            return json.dumps({'fileable': True})

        return json.dumps({'fileable': False})


class OfficeConnectorAttachPayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Consists of the minimal instruction set with which to perform an attach to
    email action.
    """
    def render(self):
        self.request.response.setHeader('Content-type', 'application/json')
        payloads = self.get_base_payloads()
        payloads_by_parent = group_payloads_by_parent(payloads, self.request)

        for container_uuid, payloads in payloads_by_parent.items():

            if container_uuid and not is_workspace_feature_enabled():
                dossier = api.content.get(UID=container_uuid)
                documents = [p['document'] for p in payloads]
                notify(DossierAttachedToEmailEvent(dossier, documents))

            for payload in payloads:
                document = payload['document']
                payload['title'] = document.title_or_id()
                payload['content-type'] = document.get_file().contentType
                payload['download'] = document.get_download_view_name()
                payload['filename'] = document.get_filename()
                del payload['document']
                notify(FileAttachedToEmailEvent(document))

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
                    payload['content-type'] = IAnnotations(document).get("content-type")
                else:
                    payload['content-type'] = document.get_file().contentType

                payload['download'] = document.get_download_view_name()

                # for oneoffixx, we checkout the document to fall in the normal
                # checkout-checkin cycle.
                if document.is_shadow_document():
                    payload['filename'] = IAnnotations(document).get("filename")
                else:
                    payload['filename'] = document.get_filename()

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
                payload['cancelcheckout'] = '@cancelcheckout'
                payload['has_pending_changes'] = document.has_pending_changes

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
