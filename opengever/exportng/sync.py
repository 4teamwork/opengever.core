import opengever.ogds.base  # isort:skip # noqa fix cyclic import
from Acquisition import aq_parent
from collections import namedtuple
from datetime import date
from datetime import datetime
from DateTime import DateTime
from opengever.base.interfaces import IReferenceNumber
from opengever.exportng.db import create_table
from opengever.exportng.db import engine
from opengever.exportng.db import metadata
from opengever.exportng.utils import userid_to_email
from opengever.exportng.journal import get_journal_entries_from_document
from opengever.exportng.journal import get_journal_entries_from_dossier
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone import api
from plone.dexterity.utils import iterSchemata
from Products.CMFEditions.utilities import dereference
from sqlalchemy import bindparam
from sqlalchemy import delete
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.sql.expression import false
from time import time
from zope.schema import getFields
import logging
import os.path

logger = logging.getLogger('opengever.exportng')


Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type', 'getter'],
)

SQL_CHUNK_SIZE = 5000
BLOB_VERSION_KEY = 'CloneNamedFileBlobs/opengever.document.document.IDocumentSchema.file'
CACHE = {}


def timer(func=time):
    """Set up a generator returning the elapsed time since the last call """
    def gen(last=func()):
        while True:
            elapsed = func() - last
            last = func()
            yield '%.3fs' % elapsed
    return gen()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]


def rename_dict_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)
    return dict_


def dexterity_field_value(obj, attrname):
    fields = CACHE.get('dexterity_fields', {}).get(obj.portal_type, None)
    if fields is None:
        fields = {}
        for schema in iterSchemata(obj):
            fields.update(getFields(schema))
        CACHE.setdefault('dexterity_fields', {})[obj.portal_type] = fields
    field = fields.get(attrname)
    return getattr(field.interface(obj), attrname)


def as_datetime(obj, attrname):
    value = getattr(obj, attrname)
    if callable(value):
        value = value()
    if isinstance(value, date):
        value = datetime.combine(value, datetime.min.time())
    elif isinstance(value, DateTime):
        value = value.asdatetime().replace(tzinfo=None)
    return value


def get_filedata(obj, attrname):
    if obj.portal_type == 'ftw.mail.mail':
        value = getattr(obj, 'original_message')
        if not value:
            value = getattr(obj, 'message')
    else:
        value = getattr(obj, 'file')
    if value is not None:
        return {
            "filepath": value._blob.committed(),
            "filename": value.filename,
            "mime_type": value.contentType,
        }
    return None


def get_file_extension(obj, attrname):
    if obj.portal_type == 'ftw.mail.mail':
        value = getattr(obj, 'original_message')
        if not value:
            value = getattr(obj, 'message')
    else:
        value = getattr(obj, 'file')
    if value is not None:
        return os.path.splitext(value.filename)[-1][1:]


def get_creator(obj, attrname):
    return userid_to_email(obj.Creator())


def get_responsible(obj, attrname):
    userid = dexterity_field_value(obj, attrname)
    return userid_to_email(userid)


def get_reference_number(obj, attrname):
    return '.'.join(IReferenceNumber(obj).get_numbers()['repository'])


def get_dossier_reference_number(obj, attrname):
    return '.'.join(IReferenceNumber(obj).get_numbers()['dossier'])


def parent_uid(obj, attrname):
    parent = aq_parent(obj)
    # Documents in tasks are added to the dossier
    while parent.portal_type == 'opengever.task.task':
        parent = aq_parent(parent)
    return parent.UID()


def str_upper(obj, attrname):
    return getattr(obj, attrname, '').upper()


def get_public_trial(obj, attrname):
    value_mapping = {
        'unchecked': 'NOTASSESSED',
        'public': 'PUBLIC',
        'limited-public': 'LIMITEDPUBLIC',
        'private': 'PRIVATE',
    }
    return value_mapping.get(obj.public_trial)


def get_archival_value(obj, attrname):
    value_mapping = {
        'unchecked': 'NOTASSESSED',
        'prompt': 'PROMPT',
        'archival worthy': 'ARCHIVALWORTHY',
        'not archival worthy': 'NOTARCHIVALWORTHY',
        'archival worthy with sampling': 'SAMPLING'
    }
    return value_mapping.get(obj.archival_value)


def get_privacy_layer(obj, attrname):
    value_mapping = {
        'privacy_layer_yes': True,
        'privacy_layer_no': False
    }
    return value_mapping.get(obj.privacy_layer)


def get_dossier_state(obj, attrname):
    state_mapping = {
        'dossier-state-active': 'EDIT',
        'dossier-state-inactive': 'CANCELLED',
        'dossier-state-resolved': 'CLOSED'
    }
    return state_mapping.get(api.content.get_state(obj))


def get_permissions(obj, attrname):
    principals = []
    for principal, roles in obj.get_local_roles():
        if attrname in roles:
            principals.append(userid_to_email(principal))
    return principals


def get_title(obj, attrname):
    value = dexterity_field_value(obj, attrname)
    return value.replace('\n', ' ').replace('\r', '')


def get_ml_titles(obj, attrname):
    titles = {}
    for attr in ['title_de', 'title_fr', 'title_en']:
        value = dexterity_field_value(obj, attr)
        if value:
            titles[attr] = value
    return titles


def get_references(obj, attrname):
    value = dexterity_field_value(obj, attrname)
    return [ref.to_object.UID() for ref in value if ref.to_object is not None]


class CatalogSyncer(object):

    catalog_key = 'UID'
    sql_key = 'objexternalkey'

    journal_table = 'journal_entries'
    journal_mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('relatedobj', 'historyobject', 'varchar', None),
        Attribute('action', 'event', 'varchar', None),
        Attribute('time', 'timestamp', 'datetime', None),
        Attribute('actor', 'user', 'varchar', None),
        Attribute('journal', '_journal', 'varchar', None),
    ]

    def __init__(self, query=None):
        self.base_query = query or {}
        self.rtool = api.portal.get_tool('portal_repository')
        self.hstool = api.portal.get_tool('portal_historiesstorage')
        self._catalog_items = None
        self._sql_items = None

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
        version_inserts = []
        journal_inserts = []
        added_len = len(added)
        logger.info('Adding %s %s...', added_len, self.table)
        for key in added:
            item = self.catalog_items[key]
            obj = item._unrestrictedGetObject()
            inserts.append(self.get_values(obj))
            version_inserts.extend(self.get_versions(obj))
            journal_inserts.extend(self.get_journal_entries(obj))
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, added_len, 100 * float(counter) / added_len, next(lap_time),
                )
        logger.info('Processed %d items in %s.', counter, next(total_time))

        if inserts:
            table = metadata.tables[self.table]
            with engine.connect() as conn:
                for chunk in chunks(inserts, SQL_CHUNK_SIZE):
                    conn.execute(table.insert(), chunk)
        logger.info('Added %s: %s', self.table, len(added))

        if version_inserts:
            table = metadata.tables[self.versions_table]
            with engine.connect() as conn:
                for chunk in chunks(version_inserts, SQL_CHUNK_SIZE):
                    conn.execute(table.insert(), chunk)
            logger.info('Added %s: %s', table, len(version_inserts))

        if journal_inserts:
            table = metadata.tables[self.journal_table]
            with engine.connect() as conn:
                for chunk in chunks(journal_inserts, SQL_CHUNK_SIZE):
                    conn.execute(table.insert(), chunk)
            logger.info('Added %s: %s', table, len(journal_inserts))

    def update_objects(self, modified):
        total_time = timer()
        lap_time = timer()
        counter = 0

        updates = []
        modified_len = len(modified)
        logger.info('Modifying %s %s...', modified_len, self.table)
        for key in modified:
            item = self.catalog_items[key]
            obj = item._unrestrictedGetObject()
            updates.append(rename_dict_key(self.get_values(obj), self.sql_key, 'b_key'))
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, modified_len, 100 * float(counter) / modified_len, next(lap_time),
                )
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

    def get_values(self, obj):
        data = {}
        for attr in self.mapping:
            if attr.getter is not None:
                value = attr.getter(obj, attr.name)
            else:
                try:
                    value = getattr(obj, attr.name)
                except AttributeError:
                    value = None
                if callable(value):
                    value = value()
            data[attr.col_name] = value
        data['_modified_at'] = datetime.now()
        return data

    def get_fields(self, obj):
        fields = {}
        for schema in iterSchemata(obj):
            fields.update(getFields(schema))
        return fields

    def get_versions(self, obj):
        return []

    def get_journal_entries(self, obj):
        return []


class FileplanEntrySyncer(CatalogSyncer):

    table = 'fileplanentries'
    query = {
        'portal_type': 'opengever.repository.repositoryfolder',
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('created', 'objcreatedat', 'datetime', as_datetime),
        Attribute('modified', 'objmodifiedat', 'datetime', as_datetime),
        Attribute('title', 'fcstitle', 'jsonb', get_ml_titles),
        Attribute('description', 'fcsdescription', 'varchar', None),
        Attribute('location', 'felocation', 'varchar', None),
        Attribute('reference', 'fcsbusinessnumber', 'varchar', get_reference_number),
        Attribute('valid_from', 'objvalidfrom', 'date', None),
        Attribute('valid_until', 'objvaliduntil', 'date', None),
        # Attribute('external_reference', 'boforeignnumber', 'varchar', None),
    ]


class DossierSyncer(CatalogSyncer):

    table = 'dossiers'
    query = {
        'portal_type': 'opengever.dossier.businesscasedossier',
        'is_subdossier': False,
        'review_state': [
            'dossier-state-active',
            'dossier-state-resolved',
        ],
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('created', 'objcreatedat', 'datetime', as_datetime),
        Attribute('modified', 'objmodifieddate', 'datetime', as_datetime),
        # Attribute('changed', 'changed', 'datetime', None)
        # Attribute('touched', 'touched', 'datetime', None)
        Attribute('title', 'botitle', 'varchar', get_title),
        Attribute('description', 'bodescription', 'varchar', None),
        Attribute('Creator', 'objcreatedby', 'varchar', get_creator),
        Attribute('review_state', 'bostate', 'varchar', get_dossier_state),
        Attribute('keywords', 'objterms', 'jsonb', dexterity_field_value),
        Attribute('start', 'objvalidfrom', 'date', dexterity_field_value),
        Attribute('end', 'objvalidto', 'date', dexterity_field_value),
        Attribute('responsible', 'gboresponsible', 'varchar', get_responsible),
        Attribute('external_reference', 'boforeignnumber', 'varchar', None),
        Attribute('relatedDossier', 'gborelateddossiers', 'jsonb', get_references),
        # Attribute('former_reference_number', 'bonumberhistory', 'varchar', None),
        Attribute('reference_number', 'documentnumber', 'varchar', get_dossier_reference_number),
        # Attribute('dossier_type', 'dossier_type', 'varchar', None),
        Attribute('classification', 'classification', 'varchar', str_upper),
        Attribute('privacy_layer', 'privacyprotection', 'boolean', get_privacy_layer),
        Attribute('public_trial', 'disclosurestatus', 'varchar', get_public_trial),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar', None),
        Attribute('retention_period', 'retentionperiod', 'integer', None),
        Attribute('retention_period_annotation', 'retentionperiodcomment', 'varchar', None),
        Attribute('archival_value', 'archivalvalue', 'varchar', get_archival_value),
        Attribute('archival_value_annotation', 'archivalvaluecomment', 'varchar', None),
        Attribute('custody_period', 'regularsafeguardperiod', 'integer', None),
        Attribute('Reader', 'objsecread', 'jsonb', get_permissions),
        Attribute('Editor', 'objsecchange', 'jsonb', get_permissions),
        Attribute('DossierManager', 'fadmins', 'jsonb', get_permissions),
    ]

    def get_journal_entries(self, obj):
        return get_journal_entries_from_dossier(obj)


class SubdossierSyncer(DossierSyncer):

    table = 'subdossiers'
    query = {
        'portal_type': 'opengever.dossier.businesscasedossier',
        'is_subdossier': True,
        'review_state': [
            'dossier-state-active',
            'dossier-state-resolved',
        ],
    }


class DocumentSyncer(CatalogSyncer):

    table = 'documents'
    query = {
        'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
        'trashed': False,
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('created', 'objcreatedat', 'datetime', as_datetime),
        Attribute('modified', 'objmodifieddate', 'datetime', as_datetime),
        Attribute('title', 'objname', 'varchar', get_title),
        Attribute('Creator', 'objcreatedby', 'varchar', get_creator),
        # Attribute('changed', 'changed', 'datetime', None)
        Attribute('privacy_layer', 'privacyprotection', 'boolean', get_privacy_layer),
        Attribute('public_trial', 'disclosurestatus', 'varchar', get_public_trial),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar', None),
        # Attribute('relatedItems', 'XXX', 'varchar', None),
        Attribute('description', 'dadescription', 'varchar', None),
        Attribute('keywords', 'objterms', 'jsonb', dexterity_field_value),
        Attribute('foreign_reference', 'gcexternalreference', 'varchar', None),
        Attribute('document_date', 'dadate', 'date', None),
        Attribute('receipt_date', 'gcreceiptdate', 'date', None),
        Attribute('delivery_date', 'gcdeliverydate', 'date', None),
        Attribute('document_author', 'gcauthor', 'varchar', None),
        Attribute('extension', 'extension', 'varchar', get_file_extension),
        # Attribute('document_type', 'XXX', 'date', None),
        Attribute('preserved_as_paper', 'gcpreservedaspaper', 'boolean', dexterity_field_value),
    ]
    versions_table = 'document_versions'
    versions_mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('version', 'version', 'integer', None),
        Attribute('filepath', 'filepath', 'varchar', None),
        Attribute('filname', 'filename', 'varchar', None),
        Attribute('filesize', 'filesize', 'bigint', None),
        Attribute('principal', 'versby', 'varchar', None),
        Attribute('timestamp', 'verschangedat', 'datetime', None),
        Attribute('comment', 'versdesc', 'varchar', None),
    ]

    def get_versions(self, obj):
        versions = []
        uid = obj.UID()
        history = self.rtool.getHistory(obj)
        if len(history) > 0:
            obj, history_id = dereference(obj=obj)
            for version in range(len(history)):
                vdata = self.hstool.retrieve(history_id, selector=version)
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
            data = get_filedata(obj, None)
            if data is not None:
                versions.append({
                    'objexternalkey': uid,
                    'version': 0,
                    'filepath': data['filepath'],
                    'filename': data['filename'],
                    'filesize': os.stat(data['filepath']).st_size,
                    'versby': userid_to_email(obj.Creator()),
                    'verschangedat': as_datetime(obj, 'modified'),
                    'versdesc': '',
                })
        return versions

    def get_journal_entries(self, obj):
        return get_journal_entries_from_document(obj)


class OGDSSyncer(object):

    def get_sql_items(self):
        table = metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_ogds_items(self):
        distinct_attr = getattr(self.model, self.key)
        return self.model.query.distinct(distinct_attr).all()

    def get_values(self, item):
        data = {}
        for attr in self.mapping:
            data[attr.col_name] = getattr(item, attr.name)
        return data

    def truncate(self):
        with engine.begin() as conn:
            conn.execution_options(autocommit=True).execute(
                "TRUNCATE TABLE {}".format(self.table))

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            inserts.append(self.get_values(item))

        table = metadata.tables[self.table]
        with engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


class UserSyncer(OGDSSyncer):

    table = 'users'
    model = User
    key = 'email'

    mapping = [
        Attribute('email', 'email', 'varchar', None),
        Attribute('firstname', 'firstname', 'varchar', None),
        Attribute('lastname', 'lastname', 'varchar', None),
        Attribute('active', 'active', 'boolean', None),
    ]


class GroupSyncer(OGDSSyncer):

    table = 'groups'
    model = Group
    key = 'groupname'

    mapping = [
        Attribute('groupname', 'groupname', 'varchar', None),
        Attribute('title', 'title', 'varchar', None),
        Attribute('active', 'active', 'boolean', None),
    ]


class Syncer(object):

    def __init__(self, path=None):
        self.query = {}
        if path is not None:
            self.query['path'] = {'query': path, 'depth': -1}

    def create_tables(self):
        create_table(UserSyncer.table, UserSyncer.mapping)
        create_table(GroupSyncer.table, GroupSyncer.mapping)
        create_table(CatalogSyncer.journal_table, CatalogSyncer.journal_mapping)
        create_table(FileplanEntrySyncer.table, FileplanEntrySyncer.mapping)
        create_table(DossierSyncer.table, DossierSyncer.mapping)
        create_table(SubdossierSyncer.table, SubdossierSyncer.mapping)
        create_table(DocumentSyncer.table, DocumentSyncer.mapping)
        create_table(DocumentSyncer.versions_table, DocumentSyncer.versions_mapping)
        metadata.create_all(checkfirst=True)

    def sync(self):
        UserSyncer().sync()
        GroupSyncer().sync()
        FileplanEntrySyncer(self.query).sync()
        DossierSyncer(self.query).sync()
        SubdossierSyncer(self.query).sync()
        DocumentSyncer(self.query).sync()
        self.cleanup_orphans()

    def cleanup_orphans(self):
        keys = set([])
        for table in [
            FileplanEntrySyncer.table,
            DossierSyncer.table,
            SubdossierSyncer.table,
        ]:
            sqltable = metadata.tables[table]
            stmt = select([sqltable.c.objexternalkey])
            with engine.connect() as conn:
                keys.update([r[0] for r in conn.execute(stmt).fetchall()])

        for table in [
            DossierSyncer.table,
            SubdossierSyncer.table,
            DocumentSyncer.table,
        ]:
            sqltable = metadata.tables[table]
            stmt = select([sqltable.c.objexternalkey, sqltable.c.objprimaryrelated])
            with engine.connect() as conn:
                res = conn.execute(stmt).fetchall()
                parents = dict([r for r in res])
            orphans = set(parents.values()) - keys
            if orphans:
                orphan_keys = [k for k, p in parents.items() if p in orphans]
                logger.info('Orphans: %s', orphan_keys)
                stmt = delete(sqltable).where(sqltable.c.objexternalkey.in_(orphan_keys))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, table)
                keys -= set(orphan_keys)
                if table == 'documents':
                    versions_table = metadata.tables[DocumentSyncer.versions_table]
                    stmt = delete(versions_table).where(versions_table.c.objexternalkey.in_(orphan_keys))
                    with engine.connect() as conn:
                        res = conn.execute(stmt)
                        logger.info('Removed %s orphans from table %s.', res.rowcount, DocumentSyncer.versions_table)
                journal_table = metadata.tables[CatalogSyncer.journal_table]
                stmt = delete(journal_table).where(or_(
                    journal_table.c.objexternalkey.in_(orphan_keys),
                    journal_table.c.historyobject.in_(orphan_keys)))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, CatalogSyncer.journal_table)
