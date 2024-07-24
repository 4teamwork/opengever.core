from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import create_session
from opengever.dossiertransfer.api.base import DossierTransfersBase
from opengever.dossiertransfer.api.schemas import IDossierTransferAPISchema
from opengever.dossiertransfer.model import DossierTransfer
from opengever.dossiertransfer.model import TRANSFER_STATE_PENDING
from opengever.journal.handlers import journal_entry_factory
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides


_ = MessageFactory('opengever.dossiertransfer')


class DossierTransfersPost(DossierTransfersBase):
    """API endpoint to create a new dossier transfer.

    POST /@dossier-transfers HTTP/1.1
    """

    def check_permission(self):
        super(DossierTransfersPost, self).check_permission()
        root_uid = json_body(self.request).get('root')
        root_obj = api.content.uuidToObject(root_uid)
        if root_obj and api.user.has_permission('View', obj=root_obj):
            return

        raise Unauthorized()

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        transfer_data = json_body(self.request)
        scrub_json_payload(transfer_data, IDossierTransferAPISchema)
        errors = get_validation_errors(transfer_data, IDossierTransferAPISchema)

        if errors:
            # Structure errors in a way that they can get serialized and
            # translated by the handler in opengever.api.errors
            structured_errors = [{
                'field': field,
                'error': exc.__class__.__name__,
                'message': exc.__class__.__doc__.strip()}
                for field, exc in errors
            ]
            raise BadRequest(structured_errors)

        transfer = DossierTransfer(
            title=transfer_data['title'],
            message=transfer_data.get('message', u''),
            expires=transfer_data['expires'],
            state=TRANSFER_STATE_PENDING,
            source=get_current_admin_unit(),
            target_id=transfer_data['target'],
            source_user=ogds_service().fetch_user(api.user.get_current().id),
            root=transfer_data['root'],
            documents=transfer_data.get('documents', []),
            participations=transfer_data.get('participations', []),
            all_documents=transfer_data['all_documents'],
            all_participations=transfer_data['all_participations'],
        )

        session = create_session()
        session.add(transfer)
        session.flush()

        token = transfer.issue_token()
        if not (transfer.token == token and transfer.is_valid_token(token)):
            raise Unauthorized

        serialized_transfer = self.serialize(transfer)

        self.add_journal_entry(transfer)
        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', serialized_transfer['@id'])

        return serialized_transfer

    def add_journal_entry(self, transferred_dossier):
        root_uid = json_body(self.request).get('root')
        root_obj = api.content.uuidToObject(root_uid)

        if not root_obj:
            return

        target_unit_title = safe_unicode(transferred_dossier.target.title)
        transfer_id = safe_unicode(transferred_dossier.id)
        title = _(
            u'label_journal_entry_dossier_transferred_for_source_dossier',
            default='Dossier was handed over to ${target_unit_title}. (Transfer-ID: ${transfer_id})',
            mapping=dict(
                transfer_id=transfer_id,
                target_unit_title=target_unit_title
            )
        )

        journal_entry_factory(
            root_obj,
            "Dossier transferred for source",
            title=title)
