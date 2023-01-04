from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.upgrade import ProgressLogger
from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.contact.models import URL
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import join
from sqlalchemy.sql.expression import table
from urlparse import urlparse
from zope.sqlalchemy.datamanager import mark_changed
import logging


logger = logging.getLogger('opengever.contact')
logger.setLevel(logging.INFO)


class ObjectSyncerProgressLogger(ProgressLogger):
    """Provide a custom progress-logger that can log iterables without
    a predefined length.
    """

    security = ClassSecurityInformation()

    def __init__(self, message, iterable, logger=None, timeout=5):
        self.logger = logger or logging.getLogger('opengever.contact')
        self.message = message
        self.iterable = iterable

        self.timeout = timeout
        self._timestamp = None
        self._counter = 0

    security.declarePrivate('__call__')

    def __call__(self):
        self._counter += 1
        if not self.should_be_logged():
            return

        self.logger.info('%s: %s' % (self._counter, self.message))


class SQLObjectSyncer(object):
    """The SQLObjectSyncer supports syncing an sql-table with data from
    a separate DB. Currently used for syncing contact data.
    """

    # Needs to be defined by the subclass
    # ORM Model class
    model = None
    # attributename/value pairs which are set for all objects.
    default_values = {}
    # columnname/value pair of all attributes to update/add
    attributes = {}
    source_id_column = None
    gever_id_column = None

    def __init__(self, source_session, query):
        """Expects a SQLAlchemy session to the source db and the
        corresponding select query to fetch the source data.
        """
        self.db_session = create_session()
        self.source_session = source_session

        self.query = query

    def __call__(self):
        logger.info('Start syncing {}'.format(self.model.__tablename__))

        existing_id_lookup = self.get_existing_id_lookup()
        result = self.source_session.execute(self.query)
        to_insert, to_update = self.prepare_values(result, existing_id_lookup)

        self.db_session.bulk_insert_mappings(
            self.model, to_insert, return_defaults=True)
        logger.info('{} new {} added'.format(
            len(to_insert), self.model.__tablename__))

        self.db_session.bulk_update_mappings(self.model, to_update)
        logger.info('{} {} updated'.format(
            len(to_update), self.model.__tablename__))

        if to_insert or to_update:
            mark_changed(self.db_session)

    def get_identifier(self, source_row):
        return getattr(source_row, self.source_id_column)

    def prepare_values(self, result, existing_id_lookup):
        to_insert = []
        to_update = []

        iterable = ObjectSyncerProgressLogger(
            "Preparing values {}".format(self.model.__tablename__), result)

        for source_row in iterable:
            data = self.default_values.copy()
            for key, source_key in self.attributes.items():
                if callable(source_key):
                    value = source_key(source_row)
                else:
                    value = getattr(source_row, source_key)

                if isinstance(value, str):
                    value = safe_unicode(value)

                data[key] = value

            if self.is_existing(source_row, existing_id_lookup):
                data = self.finalize_update_data(
                    data, source_row, existing_id_lookup)
                to_update.append(data)
            else:
                to_insert.append(self.finalize_insert_data(data, source_row))

        return to_insert, to_update

    def finalize_update_data(self, data, source_row, existing_id_lookup):
        data[self.gever_id_column] = existing_id_lookup[
            self.get_identifier(source_row)]
        return data

    def finalize_insert_data(self, data, source_row):
        return data

    def is_existing(self, source_row, existing_id_lookup):
        return self.get_identifier(source_row) in existing_id_lookup

    def get_existing_id_lookup(self):
        """Returns a lookup-table of all rows currently stored in gever.
        The lookup table is a dict where the key is the source identfier and
        the value is the gever-id.
        """
        raise NotImplementedError


class OrganizationSyncer(SQLObjectSyncer):

    model = Organization
    default_values = {'contact_type': 'organization'}
    attributes = {'name': 'name',
                  'description': 'description',
                  'former_contact_id': 'former_contact_id',
                  'is_active': lambda row: bool(getattr(row, 'is_active'))}

    source_id_column = 'former_contact_id'
    gever_id_column = 'contact_id'

    def get_existing_id_lookup(self):
        contact_table = table(
            "contacts",
            column('id'),
            column('former_contact_id'))
        stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
        return {key: value for (key, value) in self.db_session.execute(stmt)}

    def finalize_update_data(self, data, source_row, existing):
        data = super(OrganizationSyncer, self).finalize_update_data(
            data, source_row, existing)

        # Because Organization is a inherited Model we also need to pass in the
        # id as the organization primary key.
        data['organization_id'] = existing[self.get_identifier(source_row)]
        return data


class PersonSyncer(SQLObjectSyncer):

    model = Person
    default_values = {'contact_type': 'person'}
    attributes = {'salutation': 'salutation',
                  'academic_title': 'title',
                  'firstname': 'firstname',
                  'lastname': 'lastname',
                  'description': 'description',
                  'former_contact_id': 'former_contact_id',
                  'is_active': lambda row: bool(getattr(row, 'is_active'))}

    source_id_column = 'former_contact_id'
    gever_id_column = 'contact_id'

    def get_existing_id_lookup(self):
        contact_table = table(
            "contacts",
            column('id'),
            column('former_contact_id'))
        stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
        return {key: value for (key, value) in self.db_session.execute(stmt)}

    def finalize_update_data(self, data, source_row, existing):
        data = super(PersonSyncer, self).finalize_update_data(
            data, source_row, existing)

        # Because Person is a inherited Model we also need to pass in the
        # id as the person primary key.
        data['person_id'] = existing[self.get_identifier(source_row)]
        return data


class ContactAdditionsSyncer(SQLObjectSyncer):
    """Specific syncer class for objects which are in a n:1 relation with a
    contact for example mail addresses or phonenumbers.
    """

    _contact_mapping = None

    def get_identifier(self, source_row):
        return u'{}:{}'.format(safe_unicode(source_row.label),
                               source_row.former_contact_id)

    def get_contact_mapping(self):
        if not self._contact_mapping:
            contact_table = table(
                "contacts",
                column('id'),
                column('former_contact_id'))
            stmt = select([contact_table.c.former_contact_id, contact_table.c.id])
            self._contact_mapping = {key: value for (key, value)
                                     in self.db_session.execute(stmt)}

        return self._contact_mapping

    def finalize_insert_data(self, data, source_row):
        data['contact_id'] = self.get_contact_mapping()[
            source_row.former_contact_id]
        return data


class MailSyncer(ContactAdditionsSyncer):

    model = MailAddress
    attributes = {'label': 'label', 'address': 'address'}
    gever_id_column = 'mailaddress_id'
    _contact_mapping = None

    def get_existing_id_lookup(self):
        mail_table = table(
            "mail_addresses", column('id'),
            column('label'),
            column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            mail_table.c.id, mail_table.c.label,
            mail_table.c.contact_id, contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(mail_table, contact_table,
                 mail_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(gever_row): gever_row.id
                for gever_row in self.db_session.execute(stmt)}


def save_url(url):
    if not urlparse(url).scheme:
        return u'http://{}'.format(safe_unicode(url))

    return url


class UrlSyncer(ContactAdditionsSyncer):

    model = URL
    attributes = {'label': 'label',
                  'url': lambda row: save_url(getattr(row, 'url'))}
    gever_id_column = 'url_id'

    def get_existing_id_lookup(self):
        url_table = table(
            "urls", column('id'), column('label'), column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            url_table.c.id, url_table.c.label, url_table.c.contact_id,
            contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(url_table, contact_table,
                 url_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(gever_row): gever_row.id
                for gever_row in self.db_session.execute(stmt)}


class PhoneNumberSyncer(ContactAdditionsSyncer):

    model = PhoneNumber
    attributes = {'label': 'label',
                  'phone_number': 'phone_number'}
    gever_id_column = 'phone_number_id'

    def get_existing_id_lookup(self):
        phone_table = table(
            "phonenumbers",
            column('id'),
            column('label'),
            column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            phone_table.c.id,
            phone_table.c.label,
            phone_table.c.contact_id,
            contact_table.c.former_contact_id])

        stmt = stmt.select_from(
            join(phone_table, contact_table,
                 phone_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(gever_row): gever_row.id
                for gever_row in self.db_session.execute(stmt)}


class AddressSyncer(ContactAdditionsSyncer):

    model = Address
    attributes = {'label': 'label',
                  'street': 'street',
                  'zip_code': 'zip_code',
                  'city': 'city',
                  'country': 'country'}
    gever_id_column = 'address_id'

    def get_existing_id_lookup(self):
        address_table = table(
            "addresses", column('id'), column('label'), column('contact_id'))

        contact_table = table(
            "contacts",
            column('id'), column('former_contact_id'))

        stmt = select([
            address_table.c.id,
            address_table.c.label,
            address_table.c.contact_id,
            contact_table.c.former_contact_id])
        stmt = stmt.select_from(
            join(address_table, contact_table,
                 address_table.c.contact_id == contact_table.c.id))

        return {self.get_identifier(gever_row): gever_row.id
                for gever_row in self.db_session.execute(stmt)}
