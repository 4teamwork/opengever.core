from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from opengever.api.validation import get_validation_errors
from opengever.base.model import create_session
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossiertransfer import is_dossier_transfer_feature_enabled
from opengever.dossiertransfer.api.schemas import IPerformDossierTransferAPISchema
from opengever.dossiertransfer.model import DossierTransfer
from opengever.dossiertransfer.model import TRANSFER_STATE_COMPLETED
from opengever.kub.client import KuBClient
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.propertysheets.assignment import get_document_assignment_slots
from opengever.propertysheets.assignment import get_dossier_assignment_slots
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from Products.CMFPlone.utils import safe_hasattr
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import InternalError
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent
import json
import logging
import os.path
import requests
import shutil
import tempfile
import transaction


logger = logging.getLogger('opengever.dossiertransfer')


class PerformDossierTransfer(Service):
    """API endpoint to perform a dossier transfer.

    Creates a dossier in the repository folder given by the context.

    POST /@perform-dossier-transfer HTTP/1.1

    {
      "transfer_id": <transfer_id>
    }
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if not is_dossier_transfer_feature_enabled():
            raise BadRequest("Feature 'dossier_transfers' is not enabled.")

        if not self.is_inbox_user():
            raise Forbidden('Not an inbox user')

        data = json_body(self.request)
        errors = get_validation_errors(data, IPerformDossierTransferAPISchema)

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

        self.transfer_id = data['transfer_id']

        self.transfer = self.locate_transfer()
        if self.transfer is None:
            raise BadRequest('Unknown Transfer')

        self.fetch_and_create()

        session = create_session()
        transfer = session.query(DossierTransfer).get(self.transfer_id)
        transfer.state = TRANSFER_STATE_COMPLETED

        serializer = queryMultiAdapter(
            (self.root_obj, self.request), ISerializeToJson)
        serialized_obj = serializer()
        serialized_obj["@id"] = self.root_obj.absolute_url()
        self.request.response.setStatus(201)
        return serialized_obj

    @property
    def headers(self):
        return {
            'Accept': 'application/json',
            'X-GEVER-Dossier-Transfer-Token': self.transfer.token,
        }

    def fetch_and_create(self):
        self.tempdir = None  # Temporary directory for storing downloaded docs
        self.documents = {}  # File paths of downloaded documents by UID
        self.root_obj = None  # Created root object which we return as response
        self.objects_by_path = {}  # Created objects by source path
        self.contact_id_mapping = {}  # Source contact id => target contact id

        self.metadata = self.fetch_metadata()
        if self.metadata is None:
            raise InternalError('Could not fetch transfer metadata')

        try:
            self.fetch_documents()
            self.create_contacts()
            # Sync DB to reduce conflict propability
            transaction.begin()
            self.create_dossiers()
            self.create_documents()
        finally:
            self.cleanup()

    def locate_transfer(self):
        local_unit_id = get_current_admin_unit().unit_id
        query = DossierTransfer.query.filter(
            DossierTransfer.id == self.transfer_id
        ).filter(
            DossierTransfer.target_id == local_unit_id)
        return query.first()

    def is_inbox_user(self):
        user_id = api.user.get_current().getId()
        ogds_user = ogds_service().fetch_user(user_id)
        local_unit = get_current_admin_unit()
        for org_unit in local_unit.org_units:
            if ogds_user in org_unit.inbox_group.users:
                return True
        return False

    def fetch_metadata(self):
        url = '{}/@dossier-transfers/{}?full_content=1'.format(
            self.transfer.source.site_url, self.transfer_id)
        try:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception('Could not fetch transfer metadata.')
            return None
        return json.loads(resp.content)

    def fetch_documents(self):
        self.tempdir = tempfile.mkdtemp()
        for doc in self.metadata.get('content', {}).get('documents', []):
            url = '{}/@dossier-transfers/{}/blob/{}'.format(
                self.transfer.source.site_url, self.transfer_id, doc['UID'])
            filepath = os.path.join(self.tempdir, doc['UID'])
            try:
                with requests.get(url, headers=self.headers, stream=True) as resp:
                    resp.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
            except requests.RequestException:
                logger.exception('Could not fetch documents.')
                raise InternalError('Could not fetch documents')
            self.documents[doc['UID']] = filepath

    def create_dossiers(self):
        user_id = api.user.get_current().getId()
        slots = get_dossier_assignment_slots()

        for dossier in self.metadata.get('content', {}).get('dossiers', []):
            path = dossier[u'relative_path']
            parent_path = os.path.dirname(path)
            parent = self.objects_by_path.setdefault(parent_path, self.context)

            dossier['responsible'] = user_id
            self.strip_unknown_custom_properties(dossier, slots)

            obj = self.create_content(parent, dossier)
            self.objects_by_path[path] = obj
            if self.root_obj is None:
                self.root_obj = obj

            for participation in dossier.get('participations', []):
                self.add_participation(obj, participation)

    def create_documents(self):
        slots = get_document_assignment_slots()

        for doc in self.metadata.get('content', {}).get('documents', []):
            path = doc[u'relative_path']
            parent_path = os.path.dirname(path)
            parent = self.objects_by_path.setdefault(parent_path, self.context)

            self.strip_unknown_custom_properties(doc, slots)

            doc_file = open(self.documents[doc['UID']], 'rb')

            if doc['@type'] == 'ftw.mail.mail':
                doc['message']['data'] = doc_file
            else:
                doc['file']['data'] = doc_file

            self.objects_by_path[path] = self.create_content(parent, doc)
            doc_file.close()

    def create_content(self, parent, data):
        obj = create(parent, data['@type'], title=data['title'])

        temporarily_wrapped = False
        if IAcquirer.providedBy(obj) and not safe_hasattr(obj, "aq_base"):
            obj = obj.__of__(parent)
            temporarily_wrapped = True

        deserializer = getMultiAdapter((obj, self.request), IDeserializeFromJson)
        deserializer(validate_all=True, data=data, create=True)
        if temporarily_wrapped:
            obj = aq_base(obj)

        notify(ObjectCreatedEvent(obj))

        obj = add(parent, obj, rename=True)
        return obj

    def add_participation(self, dossier, participation):
        participant_id, roles = participation
        participant_id = self.contact_id_mapping.get(participant_id, participant_id)
        IParticipationAware(dossier).add_participation(participant_id, roles)

    def create_contacts(self):
        kub = KuBClient()

        for contact_id, contact_data in (
            self.metadata.get("content", {}).get("contacts", {}).items()
        ):
            self.contact_id_mapping[contact_id] = PersonContactSyncer(kub).sync(contact_id,
                                                                                contact_data)

    def cleanup(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def strip_unknown_custom_properties(self, data, slots):
        custom_properties = data.get('custom_properties', None)
        if not custom_properties:
            return

        for slot, fields in custom_properties.items():
            if slot not in slots:
                del data['custom_properties'][slot]
                continue

            definition = PropertySheetSchemaStorage().query(slot)
            if definition is None:
                del data['custom_properties'][slot]
                continue

            fieldnames = definition.get_fieldnames()
            for field in fields.keys():
                if field not in fieldnames:
                    del data['custom_properties'][slot][field]


class PersonContactSyncer(object):
    def __init__(self, kub_client):
        self.kub_client = kub_client

    def find_by_third_party_id(self):
        response = self.kub_client.list_people(filters={'third_party_id': self.third_party_id})
        if response['count'] == 1:
            return response["results"][0]
        return None

    def create(self):
        created_data = self.kub_client.create_person(self.contact_data)
        if created_data is None:
            raise InternalError('Creating person failed')
        return created_data

    def get_or_create_kub_obj(self):
        kub_obj = self.find_by_third_party_id()
        if not kub_obj:
            kub_obj = self.create()
        return kub_obj

    def sync(self, contact_id, contact_data):
        """Tries to find a contact in the local KUB installation and returns
        its type-id. If no contact could be found, it will create a new one.
        """
        self.contact_data = contact_data
        self.third_party_id = contact_data.get('thirdPartyId') or contact_id
        kub_obj = self.get_or_create_kub_obj()
        return 'person:{}'.format(kub_obj['id'])
