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
from opengever.ogds.models.group import Group
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone import api
from plone.dexterity.utils import iterSchemata
from Products.CMFEditions.utilities import dereference
from sqlalchemy import bindparam
from sqlalchemy import delete
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
        value = value.asdatetime()
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


def userid_to_email(userid):
    userid_email_mapping = CACHE.get('userid_email_mapping', None)
    if userid_email_mapping is None:
        users = ogds_service().all_users()
        userid_email_mapping = {user.userid: user.email for user in users}
        CACHE['userid_email_mapping'] = userid_email_mapping
    return userid_email_mapping.get(userid, userid)


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
    return aq_parent(obj).UID()


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


class CatalogSyncer(object):

    catalog_key = 'UID'
    sql_key = 'objexternalkey'

    def __init__(self, query=None):
        self.base_query = query or {}

    def get_catalog_items(self):
        query = dict(self.base_query, **self.query)
        ct = api.portal.get_tool('portal_catalog')
        return ct.unrestrictedSearchResults(query)

    def get_sql_items(self):
        table = metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def sync(self):
        logger.info('Processing %s...', self.table)
        self.init_sync()
        catalog_items = self.get_catalog_items()
        sql_items = self.get_sql_items()
        catalog_keys = set([
            getattr(item, self.catalog_key) for item in catalog_items])
        sql_keys = set([getattr(item, self.sql_key) for item in sql_items])
        catalog_items_by_key = {
            getattr(item, self.catalog_key): item for item in catalog_items}
        sql_items_by_key = {
            getattr(item, self.sql_key): item for item in sql_items}

        added = catalog_keys - sql_keys
        deleted = sql_keys - catalog_keys
        existing = catalog_keys & sql_keys

        modified = set()
        for key in existing:
            if (
                catalog_items_by_key[key].modified.asdatetime().replace(tzinfo=None)
                != sql_items_by_key[key].modified
            ):
                modified.add(key)

        total_time = timer()
        lap_time = timer()
        counter = 0

        inserts = []
        added_len = len(added)
        for key in added:
            item = catalog_items_by_key[key]
            obj = item._unrestrictedGetObject()
            inserts.append(self.get_values(obj))
            self.post_insert_obj(obj)
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, added_len, 100 * float(counter) / added_len, next(lap_time),
                )
        logger.info('Processed %d items in %s.', counter, next(total_time))

        table = metadata.tables[self.table]
        with engine.connect() as conn:
            for chunk in chunks(inserts, 5000):
                conn.execute(table.insert(), chunk)
        logger.info('Added %s: %s', table, len(added))
        self.post_insert()

        updates = []
        for key in modified:
            item = catalog_items_by_key[key]
            obj = item._unrestrictedGetObject()
            updates.append(rename_dict_key(self.get_values(obj), self.sql_key, 'b_key'))
        if updates:
            with engine.connect() as conn:
                conn.execute(table.update().where(getattr(table.c, self.sql_key) == bindparam('b_key')), updates)
        logger.info('Updated %s: %s', table, len(modified))

        deletes = []
        for key in deleted:
            deletes.append({'b_key': key, '_deleted': True})
        if deletes:
            with engine.connect() as conn:
                conn.execute(table.update().where(
                    getattr(table.c, self.sql_key) == bindparam('b_key')), deletes)
        logger.info('Deleted %s: %s', table, len(deleted))

    def get_values(self, obj):
        data = {}
        # serializer = queryMultiAdapter(
        #     (self.context, self.request), ISerializeToJson)
        # obj_data = serializer(include_items=False)
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
        return data

    def get_fields(self, obj):
        fields = {}
        for schema in iterSchemata(obj):
            fields.update(getFields(schema))
        return fields

    def init_sync(self):
        return

    def post_insert_obj(self, obj):
        return

    def post_insert(self):
        return


class FileplanEntrySyncer(CatalogSyncer):

    table = 'fileplanentries'
    query = {
        'portal_type': 'opengever.repository.repositoryfolder',
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('title', 'botitle', 'varchar', None),
        Attribute('description', 'bodescription', 'varchar', None),
        Attribute('location', 'felocation', 'varchar', None),
        Attribute('reference', 'fcsbusinessnumber', 'varchar', get_reference_number),
        # Attribute('modified', 'modified', 'datetime', as_datetime),
        Attribute('valid_from', 'objvalidfrom', 'date', None),
        Attribute('valid_until', 'objvaliduntil', 'date', None),
        # Attribute('external_reference', 'boforeignnumber', 'varchar', None),
    ]


class DossierSyncer(CatalogSyncer):

    table = 'dossiers'
    query = {
        'portal_type': 'opengever.dossier.businesscasedossier',
        'is_subdossier': False,
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('modified', 'objmodifieddate', 'datetime', as_datetime),
        # Attribute('changed', 'changed', 'datetime', None)
        # Attribute('touched', 'touched', 'datetime', None)
        Attribute('title', 'botitle', 'varchar', None),
        Attribute('description', 'bodescription', 'varchar', None),
        Attribute('Creator', 'objcreatedby', 'varchar', get_creator),
        Attribute('created', 'objcreatedat', 'datetime', as_datetime),
        Attribute('review_state', 'bostate', 'varchar', get_dossier_state),
        # Attribute('keywords', 'keywords', 'varchar', None),
        Attribute('start', 'objvalidfrom', 'date', dexterity_field_value),
        Attribute('end', 'objvalidto', 'date', dexterity_field_value),
        Attribute('responsible', 'gboresponsible', 'varchar', get_responsible),
        # Attribute('external_reference', 'boforeignnumber', 'varchar', None),
        # Attribute('relatedDossier', 'XXX', 'varchar', None),
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


class SubdossierSyncer(DossierSyncer):

    table = 'subdossiers'
    query = {
        'portal_type': 'opengever.dossier.businesscasedossier',
        'is_subdossier': True,
    }


class DocumentSyncer(CatalogSyncer):

    table = 'documents'
    query = {
        'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
    }
    mapping = [
        Attribute('UID', 'objexternalkey', 'varchar', None),
        Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
        Attribute('title', 'objname', 'varchar', None),
        Attribute('Creator', 'objcreatedby', 'varchar', get_creator),
        Attribute('created', 'objcreatedat', 'datetime', as_datetime),
        Attribute('file', '_file', 'jsonb', get_filedata),
        Attribute('extension', 'extension', 'varchar', get_file_extension),
        # Attribute('changed', 'changed', 'datetime', None)
        Attribute('privacy_layer', 'privacyprotection', 'boolean', get_privacy_layer),
        Attribute('public_trial', 'disclosurestatus', 'varchar', get_public_trial),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar', None),
        # Attribute('relatedItems', 'XXX', 'varchar', None),
        Attribute('description', 'dadescription', 'varchar', None),
        # Attribute('keywords', 'XXX', 'varchar', None),
        Attribute('foreign_reference', 'gcexternalreference', 'varchar', None),
        Attribute('document_date', 'dadate', 'date', None),
        Attribute('receipt_date', 'gcreceiptdate', 'date', None),
        Attribute('delivery_date', 'gcdeliverydate', 'date', None),
        # Attribute('document_type', 'XXX', 'date', None),
        Attribute('document_author', 'gcauthor', 'varchar', None),
        # Attribute('preserved_as_paper', 'XXX', 'varchar', None),
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

    def init_sync(self):
        self.rtool = api.portal.get_tool('portal_repository')
        self.hstool = api.portal.get_tool('portal_historiesstorage')
        self._doc_version_inserts = []

    def post_insert_obj(self, obj):
        uid = obj.UID()
        history = self.rtool.getHistory(obj)
        if len(history) > 0:
            obj, history_id = dereference(obj=obj)
            for version in range(len(history)):
                vdata = self.hstool.retrieve(history_id, selector=version)
                if 'CloneNamedFileBlobs/opengever.document.document.IDocumentSchema.file' not in vdata.referenced_data:
                    continue
                filepath = vdata.referenced_data[
                    'CloneNamedFileBlobs/opengever.document.document.IDocumentSchema.file'].committed()
                filesize = os.stat(filepath).st_size
                self._doc_version_inserts.append({
                    'objexternalkey': uid,
                    'version': version,
                    'filepath': filepath,
                    'filename': vdata.object.object.file.filename,
                    'filesize': filesize,
                    'versby': userid_to_email(vdata.metadata['sys_metadata']['principal']),
                    'verschangedat': datetime.fromtimestamp(vdata.metadata['sys_metadata']['timestamp']),
                    'versdesc': vdata.metadata['sys_metadata']['comment'],
                })
        else:
            data = get_filedata(obj, None)
            if data is not None:
                self._doc_version_inserts.append({
                    'objexternalkey': uid,
                    'version': 0,
                    'filepath': data['filepath'],
                    'filename': data['filename'],
                    'filesize': os.stat(data['filepath']).st_size,
                    'versby': userid_to_email(obj.Creator()),
                    'verschangedat': as_datetime(obj, 'modified'),
                    'versdesc': '',
                })
        return

    def post_insert(self):
        table = metadata.tables[self.versions_table]
        with engine.connect() as conn:
            conn.execute(table.insert(), self._doc_version_inserts)
        logger.info('Added %s: %s', table, len(self._doc_version_inserts))


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
