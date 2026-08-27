# -*- coding: utf-8 -*-
import opengever.ogds.base  # isort:skip # noqa fix cyclic import
from Acquisition import aq_parent
from datetime import date
from datetime import datetime
from DateTime import DateTime
from opengever.base.interfaces import IReferenceNumber
from opengever.exportng.db import engine
from opengever.exportng.db import metadata
from opengever.exportng.journal import get_journal_entries_from_document
from opengever.exportng.journal import get_journal_entries_from_dossier
from opengever.exportng.task_pdf import TaskPDFView
from opengever.exportng.utils import Attribute
from opengever.exportng.utils import document_parent
from opengever.exportng.utils import garbage_collect
from opengever.exportng.utils import get_data_dir
from opengever.exportng.utils import json_serializable
from opengever.exportng.utils import timer
from opengever.exportng.utils import userid_to_email
from opengever.meeting.model import AgendaItem
from opengever.propertysheets.utils import get_custom_properties
from plone import api
from plone.dexterity.utils import iterSchemata
from Products.CMFEditions.utilities import dereference
from six.moves import range
from sqlalchemy import bindparam
from sqlalchemy.sql.expression import false
from zope.schema import getFields
import logging
import os.path


BLOB_VERSION_KEY = 'CloneNamedFileBlobs/opengever.document.document.IDocumentSchema.file'
CACHE = {}
SQL_CHUNK_SIZE = 5000
VERSIONS_TABLE = 'document_versions'
VERSIONS_MAPPING = [
    Attribute('UID', 'objexternalkey', 'varchar'),
    Attribute('version', 'version', 'integer'),
    Attribute('filepath', 'filepath', 'varchar'),
    Attribute('filname', 'filename', 'varchar'),
    Attribute('filesize', 'filesize', 'bigint'),
    Attribute('principal', 'versby', 'varchar'),
    Attribute('timestamp', 'verschangedat', 'datetime'),
    Attribute('comment', 'versdesc', 'varchar'),
]

logger = logging.getLogger('opengever.exportng')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def rename_dict_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)
    return dict_


class CatalogItemSerializer(object):

    has_many = False

    def __init__(self, item):
        self.item = item
        self.obj = item._unrestrictedGetObject()
        self.parent = self.get_parent()

    def ignore(self):
        return False

    def get_parent(self):
        return aq_parent(self.obj)

    def data(self):
        data = {}
        for attr in self.mapping:
            getter = getattr(self, attr.name, None)
            if getter is not None:
                value = getter()
            else:
                dxfield = self.dexterity_field(attr.name)
                if dxfield is not None:
                    value = getattr(dxfield.interface(self.obj), attr.name)
                else:
                    try:
                        value = getattr(self.obj, attr.name)
                    except AttributeError:
                        value = None
                    if callable(value):
                        value = value()
            data[attr.col_name] = value
        data['_modified_at'] = datetime.now()
        return data

    def dexterity_field(self, attrname):
        portal_type = self.obj.portal_type
        fields = CACHE.get('dexterity_fields', {}).get(portal_type, None)
        if fields is None:
            fields = {}
            for schema in iterSchemata(self.obj):
                fields.update(getFields(schema))
            CACHE.setdefault('dexterity_fields', {})[portal_type] = fields
        return fields.get(attrname)

    def dexterity_field_value(self, attrname):
        dxfield = self.dexterity_field(attrname)
        return getattr(dxfield.interface(self.obj), attrname)

    def as_datetime(self, value):
        if callable(value):
            value = value()
        if isinstance(value, date):
            value = datetime.combine(value, datetime.min.time())
        elif isinstance(value, DateTime):
            value = value.asdatetime().replace(tzinfo=None)
        return value

    def parent_uid(self):
        return self.parent.UID()

    def created(self):
        return self.as_datetime(self.obj.created())

    def modified(self):
        return self.as_datetime(self.obj.modified())

    def title(self):
        value = self.dexterity_field_value('title')
        return value.replace('\n', ' ').replace('\r', '')

    def creator(self):
        return userid_to_email(self.obj.Creator())

    def authorized_principals(self, role):
        principals = []
        for principal, roles in self.obj.get_local_roles():
            if role in roles:
                principals.append(userid_to_email(principal))
        return principals

    def readers(self):
        return self.authorized_principals('Reader')

    def editors(self):
        return self.authorized_principals('Editor')

    def managers(self):
        return self.authorized_principals('DossierManager')

    def privacy_layer(self):
        value_mapping = {
            'privacy_layer_yes': True,
            'privacy_layer_no': False
        }
        return value_mapping.get(self.dexterity_field_value('privacy_layer'))

    def public_trial(self):
        value_mapping = {
            'unchecked': 'NOTASSESSED',
            'public': 'PUBLIC',
            'limited-public': 'LIMITEDPUBLIC',
            'private': 'PRIVATE',
        }
        return value_mapping.get(self.dexterity_field_value('public_trial'))

    def archival_value(self):
        value_mapping = {
            'unchecked': 'NOTASSESSED',
            'prompt': 'PROMPT',
            'archival worthy': 'ARCHIVALWORTHY',
            'not archival worthy': 'NOTARCHIVALWORTHY',
            'archival worthy with sampling': 'SAMPLING'
        }
        return value_mapping.get(self.dexterity_field_value('archival_value'))

    def versions(self):
        return []

    def journal_entries(self):
        return []


class CatalogSyncer(object):

    catalog_key = 'UID'
    sql_key = 'objexternalkey'
    additional_tables = []

    def __init__(self, query=None):
        self.base_query = query or {}
        self._catalog_items = None
        self._sql_items = None
        self.site = api.portal.get()

    @property
    def catalog_items(self):
        if self._catalog_items is None:
            query = dict(self.base_query, **self.query)
            ct = api.portal.get_tool('portal_catalog')
            self._catalog_items = {
                getattr(item, self.catalog_key): item
                for item in ct.unrestrictedSearchResults(query)
            }
        return self._catalog_items

    @property
    def sql_items(self):
        if self._sql_items is None:
            table = metadata.tables[self.table]
            stmt = table.select().where(table.c._deleted == false())
            with engine.connect() as conn:
                self._sql_items = {
                    getattr(item, self.sql_key): item
                    for item in conn.execute(stmt).fetchall()
                }
        return self._sql_items

    def sync(self):
        logger.info('Processing %s...', self.table)
        catalog_keys = set(self.catalog_items.keys())
        sql_keys = set(self.sql_items.keys())

        added = catalog_keys - sql_keys
        deleted = sql_keys - catalog_keys
        existing = catalog_keys & sql_keys
        modified = set()
        for key in existing:
            if (
                self.catalog_items[key].modified.asdatetime().replace(tzinfo=None)
                > self.sql_items[key]._modified_at
            ):
                modified.add(key)

        self.add_objects(added)
        self.update_objects(modified)
        self.delete_objects(deleted)

    def add_objects(self, added):
        total_time = timer()
        lap_time = timer()
        counter = 0

        inserts = []
        additional_inserts = {}
        for tablename in self.additional_tables:
            additional_inserts[tablename] = []
        added_len = len(added)
        logger.info('Adding %s %s...', added_len, self.table)
        for key in added:
            item = self.catalog_items[key]
            serializer = self.serializer(item)
            if serializer.ignore():
                continue
            if serializer.has_many:
                inserts.extend(serializer.data())
            else:
                inserts.append(serializer.data())
            for table in self.additional_tables:
                getter = getattr(serializer, '{}_data'.format(table))
                additional_inserts.setdefault(table, []).extend(getter())
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, added_len, 100 * float(counter) / added_len, next(lap_time),
                )
                garbage_collect(self.site)
        logger.info('Processed %d items in %s.', counter, next(total_time))

        if inserts:
            table = metadata.tables[self.table]
            with engine.connect() as conn:
                for chunk in chunks(inserts, SQL_CHUNK_SIZE):
                    conn.execute(table.insert(), chunk)
        logger.info('Added %s: %s', self.table, len(added))

        for tablename in self.additional_tables:
            table = metadata.tables[tablename]
            with engine.connect() as conn:
                for chunk in chunks(additional_inserts[tablename], SQL_CHUNK_SIZE):
                    conn.execute(table.insert(), chunk)
            logger.info('Added %s: %s', table, len(additional_inserts[tablename]))

    def update_objects(self, modified):
        total_time = timer()
        lap_time = timer()
        counter = 0

        updates = []
        modified_len = len(modified)
        logger.info('Modifying %s %s...', modified_len, self.table)
        for key in modified:
            item = self.catalog_items[key]
            serializer = self.serializer(item)
            updates.append(rename_dict_key(serializer.data(), self.sql_key, 'b_key'))
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, modified_len, 100 * float(counter) / modified_len, next(lap_time),
                )
                garbage_collect(self.site)
        logger.info('Processed %d items in %s.', counter, next(total_time))

        if updates:
            table = metadata.tables[self.table]
            with engine.connect() as conn:
                conn.execute(table.update().where(getattr(table.c, self.sql_key) == bindparam('b_key')), updates)
        logger.info('Updated %s: %s', self.table, len(modified))

    def delete_objects(self, deleted):
        total_time = timer()
        lap_time = timer()
        counter = 0

        deletes = []
        deleted_len = len(deleted)
        logger.info('Deleting %s %s...', deleted_len, self.table)
        for key in deleted:
            deletes.append({'b_key': key, '_deleted': True})
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, deleted_len, 100 * float(counter) / deleted_len, next(lap_time),
                )
        logger.info('Processed %d items in %s.', counter, next(total_time))

        if deletes:
            table = metadata.tables[self.table]
            with engine.connect() as conn:
                conn.execute(table.update().where(
                    getattr(table.c, self.sql_key) == bindparam('b_key')), deletes)
        logger.info('Deleted %s: %s', self.table, len(deleted))


class FileplanEntrySerializer(CatalogItemSerializer):

    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar'),
        Attribute('parent_uid', 'objprimaryrelated', 'varchar'),
        Attribute('created', 'objcreatedat', 'datetime'),
        Attribute('modified', 'objmodifiedat', 'datetime'),
        Attribute('title', 'fcstitle', 'jsonb'),
        Attribute('description', 'fcsdescription', 'varchar'),
        Attribute('location', 'felocation', 'varchar'),
        Attribute('reference_number', 'fcsbusinessnumber', 'integer'),
        Attribute('valid_from', 'objvalidfrom', 'date'),
        Attribute('valid_until', 'objvaliduntil', 'date'),
        # Attribute('external_reference', 'boforeignnumber', 'varchar', None),
        Attribute('full_reference_number', '_sort_key', 'varchar'),
    ]

    def title(self):
        titles = {}
        for lang in ['de', 'fr', 'en']:
            value = self.dexterity_field_value('title_%s' % lang)
            if value:
                titles[lang] = value
        return titles

    def reference_number(self):
        return int(IReferenceNumber(self.obj).get_local_number())

    def full_reference_number(self):
        return '.'.join(IReferenceNumber(self.obj).get_numbers()['repository'])


class FileplanEntrySyncer(CatalogSyncer):

    table = 'fileplanentries'
    query = {
        'portal_type': 'opengever.repository.repositoryfolder',
    }
    serializer = FileplanEntrySerializer


class DossierSerializer(CatalogItemSerializer):

    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar'),
        Attribute('parent_uid', 'objprimaryrelated', 'varchar'),
        Attribute('created', 'objcreatedat', 'datetime'),
        Attribute('modified', 'objmodifiedat', 'datetime'),
        # Attribute('changed', 'changed', 'datetime')
        # Attribute('touched', 'touched', 'datetime')
        Attribute('title', 'botitle', 'varchar'),
        Attribute('description', 'bodescription', 'varchar'),
        Attribute('creator', 'objcreatedby', 'varchar'),
        Attribute('review_state', 'bostate', 'varchar'),
        Attribute('keywords', 'objterms', 'jsonb'),
        Attribute('start', 'objvalidfrom', 'date'),
        Attribute('end', 'objvalidto', 'date'),
        Attribute('responsible', 'gboresponsible', 'varchar'),
        Attribute('external_reference', 'boforeignnumber', 'varchar'),
        Attribute('related_dossiers', 'gborelateddossiers', 'jsonb'),
        Attribute('former_reference_number', 'bonumberhistory', 'jsonb'),
        Attribute('reference_number', 'bosequencenumber', 'integer'),
        Attribute('dossier_type', 'objcategory', 'varchar'),
        Attribute('customfields', 'customfieldsjson', 'jsonb'),
        Attribute('classification', 'classification', 'varchar'),
        Attribute('privacy_layer', 'privacyprotection', 'boolean'),
        Attribute('public_trial', 'disclosurestatus', 'varchar'),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar'),
        Attribute('retention_period', 'retentionperiod', 'integer'),
        Attribute('retention_period_annotation', 'retentionperiodcomment', 'varchar'),
        Attribute('archival_value', 'archivalvalue', 'varchar'),
        Attribute('archival_value_annotation', 'archivalvaluecomment', 'varchar'),
        Attribute('custody_period', 'regularsafeguardperiod', 'integer'),
        Attribute('readers', 'objsecread', 'jsonb'),
        Attribute('editors', 'objsecchange', 'jsonb'),
        Attribute('managers', 'fadmins', 'jsonb'),
        Attribute('sort_order', '_sort_key', 'varchar'),
    ]

    def review_state(self):
        state_mapping = {
            'dossier-state-active': 'EDIT',
            'dossier-state-inactive': 'CANCELLED',
            'dossier-state-resolved': 'CLOSED'
        }
        return state_mapping.get(api.content.get_state(self.obj))

    def responsible(self):
        return userid_to_email(self.dexterity_field_value('responsible'))

    def related_dossiers(self):
        value = self.dexterity_field_value('relatedDossier')
        return [ref.to_object.UID() for ref in value if ref.to_object is not None]

    def reference_number(self):
        return int(IReferenceNumber(self.obj).get_local_number())

    def former_reference_number(self):
        return [self.dexterity_field_value('former_reference_number')]

    def classification(self):
        return self.dexterity_field_value('classification').upper()

    def dossier_type(self):
        return None

    def customfields(self):
        return None
        if not self.dexterity_field_value('dossier_type'):
            return None
        return json_serializable(get_custom_properties(self.obj)) or None

    def sort_order(self):
        return '.'.join([str(n).zfill(4) for n in IReferenceNumber(
            self.obj).get_numbers()['dossier']])

    def journal_entries_data(self):
        return get_journal_entries_from_dossier(self.obj)


class DossierSyncer(CatalogSyncer):

    table = 'dossiers'
    additional_tables = ['journal_entries']
    query = {
        'portal_type': [
            'opengever.dossier.businesscasedossier',
            'opengever.meeting.meetingdossier',
        ],
        'is_subdossier': False,
        'review_state': [
            'dossier-state-active',
            'dossier-state-resolved',
            'dossier-state-inactive',
        ],
    }
    serializer = DossierSerializer


class SubdossierSyncer(DossierSyncer):

    table = 'subdossiers'
    query = {
        'portal_type': 'opengever.dossier.businesscasedossier',
        'is_subdossier': True,
        'review_state': [
            'dossier-state-active',
            'dossier-state-resolved',
            'dossier-state-inactive',
        ],
    }
    serializer = DossierSerializer


class DocumentSerializer(CatalogItemSerializer):

    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar'),
        Attribute('parent_uid', 'objprimaryrelated', 'varchar'),
        Attribute('created', 'objcreatedat', 'datetime'),
        Attribute('modified', 'objmodifiedat', 'datetime'),
        Attribute('title', 'objname', 'varchar'),
        Attribute('creator', 'objcreatedby', 'varchar'),
        # Attribute('changed', 'changed', 'datetime')
        Attribute('privacy_layer', 'privacyprotection', 'boolean'),
        Attribute('public_trial', 'disclosurestatus', 'varchar'),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar'),
        Attribute('description', 'dadescription', 'varchar'),
        Attribute('keywords', 'objterms', 'jsonb'),
        Attribute('reference_number', 'documentnumber', 'integer'),
        Attribute('foreign_reference', 'gcexternalreference', 'varchar'),
        Attribute('document_date', 'dadate', 'date'),
        Attribute('receipt_date', 'gcreceiptdate', 'date'),
        Attribute('delivery_date', 'gcdeliverydate', 'date'),
        Attribute('document_author', 'gcauthor', 'varchar'),
        Attribute('file_extension', 'extension', 'varchar'),
        Attribute('attributedefinitiontarget', 'attributedefinitiontarget', 'varchar'),
        Attribute('preserved_as_paper', 'gcpreservedaspaper', 'boolean'),
        Attribute('document_type', 'objcategory', 'varchar'),
        Attribute('customfields', 'customfieldsjson', 'jsonb'),
    ]

    def file_extension(self):
        if self.obj.portal_type == 'ftw.mail.mail':
            value = getattr(self.obj, 'original_message')
            if not value:
                value = getattr(self.obj, 'message')
        else:
            value = getattr(self.obj, 'file')
        if value is not None:
            return os.path.splitext(value.filename)[-1][1:]

    def get_parent(self):
        return document_parent(self.obj)

    def parent_uid(self):
        if isinstance(self.parent, AgendaItem):
            return 'agendaitem-{}'.format(self.parent.agenda_item_id)
        else:
            return self.parent.UID()

    def reference_number(self):
        return int(IReferenceNumber(self.obj).get_local_number())

    def document_type(self):
        return None

    def customfields(self):
        return None
        if not self.dexterity_field_value('document_type'):
            return None
        return get_custom_properties(self.obj) or None

    # proposals:
    # - pproposaldocument
    # - pdocuments
    # agenda items:
    # - references
    # - aidecisionword
    # meetings:
    # - mdocuments
    def attributedefinitiontarget(self):
        if isinstance(self.parent, AgendaItem):
            return 'references'
        real_parent = aq_parent(self.obj)
        if real_parent.portal_type == 'opengever.meeting.submittedproposal':
            if self.obj == real_parent.get_proposal_document():
                return 'pproposaldocument'
            else:
                return 'pdocuments'
        if self.parent.portal_type == 'opengever.meeting.proposal':
            return 'pproposaldocument'
        if self.parent.portal_type == 'opengever.dossier.businesscasedossier':
            return 'gbodocuments'
        if self.parent.portal_type == 'opengever.meeting.meetingdossier':
            return 'gbodocuments'
        logger.warning('Could not determine attributedefinitiontarget for %s', self.obj)
        return 'gbodocuments'

    def document_versions_data(self):
        versions = []
        uid = self.obj.UID()
        rtool = api.portal.get_tool('portal_repository')
        hstool = api.portal.get_tool('portal_historiesstorage')
        history = rtool.getHistory(self.obj)
        if len(history) > 0:
            obj, history_id = dereference(obj=self.obj)
            for version in range(len(history)):
                vdata = hstool.retrieve(history_id, selector=version)
                if BLOB_VERSION_KEY not in vdata.referenced_data:
                    continue
                filepath = vdata.referenced_data[BLOB_VERSION_KEY].committed()
                filesize = os.stat(filepath).st_size
                versions.append({
                    'objexternalkey': uid,
                    'version': version,
                    'filepath': filepath,
                    'filename': vdata.object.object.file.filename,
                    'filesize': filesize,
                    'versby': userid_to_email(vdata.metadata['sys_metadata']['principal']),
                    'verschangedat': datetime.fromtimestamp(vdata.metadata['sys_metadata']['timestamp']),
                    'versdesc': vdata.metadata['sys_metadata']['comment'],
                })
        if len(versions) < 1:
            data = self.get_filedata()
            if data is not None:
                versions.append({
                    'objexternalkey': uid,
                    'version': 0,
                    'filepath': data['filepath'],
                    'filename': data['filename'],
                    'filesize': os.stat(data['filepath']).st_size,
                    'versby': userid_to_email(self.obj.Creator()),
                    'verschangedat': self.as_datetime(self.obj.modified()),
                    'versdesc': '',
                })
        return versions

    def get_filedata(self):
        if self.obj.portal_type == 'ftw.mail.mail':
            value = getattr(self.obj, 'original_message')
            if not value:
                value = getattr(self.obj, 'message')
        else:
            value = getattr(self.obj, 'file')
        if value is not None:
            return {
                "filepath": value._blob.committed(),
                "filename": value.filename,
                "mime_type": value.contentType,
            }
        return None

    def journal_entries_data(self):
        return get_journal_entries_from_document(self.obj)


class DocumentSyncer(CatalogSyncer):

    table = 'documents'
    additional_tables = ['document_versions', 'journal_entries']
    query = {
        'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
        'trashed': False,
    }
    serializer = DocumentSerializer


class CommitteePeriodSerializer(CatalogItemSerializer):
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar'),
        Attribute('parent_uid', 'objprimaryrelated', 'varchar'),
        Attribute('title', 'objname', 'varchar'),
        Attribute('start', 'pdbegin', 'date'),
        Attribute('end', 'pdend', 'date'),
        # Attribute('decision_sequence_number', 'XXX', 'integer'),
        # Attribute('meeting_sequence_number', 'XXX', 'integer'),
    ]


class CommitteePeriodSyncer(CatalogSyncer):

    table = 'committee_periods'
    query = {
        'portal_type': 'opengever.meeting.period',
    }
    serializer = CommitteePeriodSerializer


tasks_by_dossier = {}


class TaskSerializer(CatalogItemSerializer):
    has_many = True
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar'),
        Attribute('objectid', 'objectid', 'varchar'),
        Attribute('title', 'objname', 'varchar'),
        Attribute('created', 'objcreatedat', 'datetime'),
        Attribute('creator', 'objcreatedby', 'varchar'),
        Attribute('activities', 'procinstactivities', 'jsonb'),
    ]

    taks_type_mapping = {
        'information': 'COO.111.100.1.2148921',  # Zur Kenntnisnahme
        'direct-execution': 'COO.111.100.1.2148922',  # Zur direkten Erledigung
        'comment': 'COO.111.100.1.2148927',  # Zur Stellungnahme
        'approval': 'COO.111.100.1.2148923',  # Zur Genehmigung
        'correction': 'COO.111.100.1.2148924',  # Zur Prüfung / Korrektur
        'report': 'COO.111.100.1.2148925',  # Zum Bericht / Antrag
    }

    state_mapping = {
        'task-state-cancelled': 'NOTEXECUTED',
        'task-state-planned': 'WAITING',
        'task-state-in-progress': 'STARTABLE',
        'task-state-open': 'STARTABLE',
        'task-state-rejected': 'NOTEXECUTED ',
        'task-state-resolved': 'COMPLETED',
        'task-state-tested-and-closed': 'COMPLETED',
    }

    def ignore(self):
        if self.obj.get_is_subtask():
            return True
        self.uid = self.obj.UID()
        self.pdf_filename = '{}.pdf'.format(self.uid)
        self.pdf_path = os.path.join(self.base_path, self.pdf_filename)
        self.create_task_pdf()
        self.dossier = self.obj.get_main_dossier()
        self.dossier_uid = self.dossier.UID()
        self.create_subdossier = False
        if self.dossier_uid not in tasks_by_dossier:
            self.create_subdossier = True
            tasks_by_dossier[self.dossier_uid] = []
        tasks_by_dossier[self.dossier_uid].append(self.uid)
        self.created_at = datetime.now()
        return False

    def create_task_pdf(self):
        view = TaskPDFView(self.obj, self.obj.REQUEST)
        pdf_content = view()
        pdf_filename = '{}.pdf'.format(self.uid)
        pdf_path = os.path.join(self.base_path, pdf_filename)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)

    def objectid(self):
        return self.get_parent().UID()

    def activities(self):
        catalog = api.portal.get_tool('portal_catalog')
        subtasks = catalog.unrestrictedSearchResults(
            portal_type='opengever.task.task',
            path={'query': '/'.join(self.obj.getPhysicalPath()), 'depth': 1},
            sort_on='getObjPositionInParent',
        )
        activity = {
            'objexternalkey': self.uid,
            'objname': self.obj.Title(),
            'actinstdefinition': self.taks_type_mapping[self.obj.task_type],
            'objcreatedby': self.creator(),
            'objcreatedat': self.created(),
            'actinstparticipant': userid_to_email(self.dexterity_field_value('responsible')),
            'actinststate': self.state_mapping[self.obj.get_review_state()],
            'actinstenddeadline': datetime.combine(self.obj.deadline, datetime.max.time()),
        }
        if activity['actinststate'] == 'COMPLETED':
            activity['actinststartedat'] = activity['objcreatedat']
            activity['actinstcompletedat'] = self.as_datetime(self.obj.modified())

        if not subtasks:
            return json_serializable([activity])

        activities = []

        is_sequential = self.obj.is_sequential_main_task()
        prev_activity = None
        for subtask in subtasks:
            obj = subtask._unrestrictedGetObject()
            activity = {
                'objexternalkey': obj.UID(),
                'objname': obj.Title(),
                'actinstdefinition': self.taks_type_mapping[obj.task_type],
                'objcreatedby': userid_to_email(obj.Creator()),
                'objcreatedat': self.as_datetime(obj.created()),
                'actinstparticipant': userid_to_email(subtask.responsible),
                'actinststate': self.state_mapping[obj.get_review_state()],
                'actinstenddeadline': datetime.combine(obj.deadline, datetime.max.time()),
            }
            if prev_activity:
                activity['actinstprev'] = [prev_activity]
            if activity['actinststate'] == 'COMPLETED':
                activity['actinststartedat'] = activity['objcreatedat']
                activity['actinstcompletedat'] = self.as_datetime(obj.modified())

            activities.append(activity)
            if is_sequential:
                prev_activity = obj.UID()

        next_activity = None
        if is_sequential:
            for activity in reversed(activities):
                if next_activity:
                    activity['actinstnext'] = [next_activity]
                next_activity = activity['objexternalkey']

        return json_serializable(activities)

    def data(self):
        data = super(TaskSerializer, self).data()
        # We have to export a task (workflow) for each document
        docs = self.obj.task_documents()
        del data['objectid']
        objectids = [doc.UID() for doc in docs]
        objectids.append('{}-doc'.format(self.obj.UID()))
        return [dict(objectid=objectid, **data) for objectid in objectids]

    def documents_data(self):
        return [{
            'objexternalkey': '{}-doc'.format(self.obj.UID()),
            'objprimaryrelated': '{}-tasks'.format(self.dossier.UID()),
            'attributedefinitiontarget': 'gbodocuments',
            'objname': self.obj.Title(),
            'objcreatedat': self.created_at.isoformat(),
            'objmodifiedat': self.created_at.isoformat(),
            'objterms': [],
        }]

    def document_versions_data(self):
        return [{
            'objexternalkey': '{}-doc'.format(self.obj.UID()),
            'version': 0,
            'filepath': self.pdf_path,
            'filename': self.pdf_filename,
            'filesize': os.stat(self.pdf_path).st_size,
            'versby': 'zopemaster',
            'verschangedat': self.created_at.isoformat(),
            'versdesc': None,
        }]

    def subdossiers_data(self):
        if self.create_subdossier:
            return [{
                'objexternalkey': '{}-tasks'.format(self.dossier.UID()),
                'objprimaryrelated': self.dossier.UID(),
                'botitle': 'Aufgaben',
                'gboresponsible': 'zopemaster',
                'objcreatedat': self.created_at.isoformat(),
                'bonumberhistory': [],
                'objterms': [],
                'gborelateddossiers': [],
                'fadmins': [],
                'objsecchange': [],
                'objsecread': [],
            }]
        else:
            return []


class TaskSyncer(CatalogSyncer):

    table = 'workflows'
    additional_tables = ['subdossiers', 'documents', 'document_versions']
    query = {
        'portal_type': 'opengever.task.task',
    }
    serializer = TaskSerializer

    def add_objects(self, added):
        self.serializer.base_path = get_data_dir('tasks')
        super(TaskSyncer, self).add_objects(added)
