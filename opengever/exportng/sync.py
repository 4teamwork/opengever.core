import opengever.ogds.base  # isort:skip # noqa fix cyclic import
from Acquisition import aq_parent
from collections import namedtuple
from opengever.base.interfaces import IReferenceNumber
from opengever.exportng.db import create_table
from opengever.exportng.db import engine
from opengever.exportng.db import metadata
from opengever.ogds.models.group import Group
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone import api
from plone.dexterity.utils import iterSchemata
from sqlalchemy import bindparam
from sqlalchemy.sql.expression import false
from zope.schema import getFields
import logging
import os.path


logger = logging.getLogger('opengever.exportng')


Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type', 'getter'],
)

CACHE = {}


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
    return value.asdatetime()


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


def userid_to_email(obj, attrname):
    userid = dexterity_field_value(obj, attrname)
    userid_email_mapping = CACHE.get('userid_email_mapping', None)
    if userid_email_mapping is None:
        users = ogds_service().all_users()
        userid_email_mapping = {user.userid: user.email for user in users}
        CACHE['userid_email_mapping'] = userid_email_mapping
    return userid_email_mapping.get(userid, userid)


def get_reference_number(obj, attrname):
    return '.'.join(IReferenceNumber(obj).get_numbers()['repository'])


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


class CatalogSyncer(object):

    catalog_key = 'UID'
    sql_key = 'objexternalkey'

    def get_catalog_items(self):
        ct = api.portal.get_tool('portal_catalog')
        return ct.unrestrictedSearchResults(**self.query)

    def get_sql_items(self):
        table = metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def sync(self):
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

        inserts = []
        for key in added:
            item = catalog_items_by_key[key]
            obj = item.getObject()
            inserts.append(self.get_values(obj))
        table = metadata.tables[self.table]
        with engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(added))

        updates = []
        for key in modified:
            item = catalog_items_by_key[key]
            obj = item.getObject()
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
        Attribute('Creator', 'objcreatedby', 'varchar', None),
        Attribute('review_sate', 'bostate', 'varchar', get_dossier_state),
        # Attribute('keywords', 'keywords', 'varchar', None),
        Attribute('start', 'objvalidfrom', 'date', None),
        Attribute('end', 'objvalidto', 'date', None),
        Attribute('responsible', 'gboresponsible', 'varchar', userid_to_email),
        # Attribute('external_reference', 'boforeignnumber', 'varchar', None),
        # Attribute('relatedDossier', 'XXX', 'varchar', None),
        # Attribute('former_reference_number', 'bonumberhistory', 'varchar', None),
        # Attribute('reference_number', 'bonumberhistory', 'varchar', None),
        # Attribute('dossier_type', 'dossier_type', 'varchar', None),
        Attribute('classification', 'classification', 'varchar', str_upper),
        Attribute('privacy_layer', 'privacyprotection', 'varchar', get_privacy_layer),
        Attribute('public_trial', 'disclosurestatus', 'varchar', get_public_trial),
        Attribute('public_trial_statement', 'disclosurestatusstatement', 'varchar', None),
        Attribute('retention_period', 'retentionperiod', 'integer', None),
        Attribute('retention_period_annotation', 'retentionperiodcomment', 'varchar', None),
        Attribute('archival_value', 'archivalvalue', 'varchar', get_archival_value),
        Attribute('archival_value_annotation', 'archivalvaluecomment', 'varchar', None),
        Attribute('custody_period', 'regularsafeguardperiod', 'varchar', None),
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
        Attribute('Creator', 'objcreatedby', 'varchar', None),
        Attribute('file', '_file', 'jsonb', get_filedata),
        Attribute('extension', 'extension', 'varchar', get_file_extension),
        # Attribute('changed', 'changed', 'datetime', None)
        Attribute('privacy_layer', 'privacyprotection', 'varchar', get_privacy_layer),
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


class OGDSSyncer(object):

    def get_sql_items(self):
        table = metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_ogds_items(self):
        return self.model.query.all()

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

    mapping = [
        Attribute('email', 'email', 'varchar', None),
        Attribute('firstname', 'firstname', 'varchar', None),
        Attribute('lastname', 'lastname', 'varchar', None),
        Attribute('active', 'active', 'boolean', None),
    ]


class GroupSyncer(OGDSSyncer):

    table = 'groups'
    model = Group

    mapping = [
        Attribute('groupname', 'groupname', 'varchar', None),
        Attribute('title', 'title', 'varchar', None),
        Attribute('active', 'active', 'boolean', None),
    ]


class Syncer(object):

    def create_tables(self):
        create_table(UserSyncer.table, UserSyncer.mapping)
        create_table(GroupSyncer.table, GroupSyncer.mapping)
        create_table(FileplanEntrySyncer.table, FileplanEntrySyncer.mapping)
        create_table(DossierSyncer.table, DossierSyncer.mapping)
        create_table(SubdossierSyncer.table, SubdossierSyncer.mapping)
        create_table(DocumentSyncer.table, DocumentSyncer.mapping)
        metadata.create_all(checkfirst=True)

    def sync(self):
        UserSyncer().sync()
        GroupSyncer().sync()
        FileplanEntrySyncer().sync()
        DossierSyncer().sync()
        SubdossierSyncer().sync()
        DocumentSyncer().sync()
