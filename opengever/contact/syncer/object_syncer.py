from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.upgrade import ProgressLogger
from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import Contact
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.contact.models import URL
from urlparse import urlparse
import logging
import transaction


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


class ObjectSyncer(object):
    """Use the Objectsyncer to sync an sql-table with data form separate DB.
    """

    keys = []  # values updated by the syncer

    type_name = ""

    total_items = 0

    internal_object = None
    remote_object = None

    def __init__(self, source_session, query):
        """data: an iterable with all queried objects (ResultProxy, list of dicts)
        """
        self.db_session = create_session()
        self.source_session = source_session
        self.stats = {'updated': 0, 'no_change': 0, 'added': 0, 'total': 0}

        self.query = query

    def __call__(self):
        """Starts the sync-process
        """
        logger.info("Syncing {}...".format(self.type_name))
        self.reset_statistic()

        self.initalize_existing_mapping()
        self.initalize_contact_id_mapping()

        result = self.source_session.execute(self.query)
        iterable = ObjectSyncerProgressLogger(
            "Syncing {}".format(self.type_name), result)

        for row in iterable:
            self.stats['total'] += 1

            internal_object = self.get_internal_obj(row)
            remote_object = self.get_remote_object(row)

            if not remote_object:
                continue

            if internal_object:
                self.update_object(remote_object, internal_object)
            else:
                self.add_object(remote_object)

        logger.info("Syncing of {} succeeded".format(self.type_name))
        self.log_statistic()

        transaction.commit()

    def initalize_existing_mapping(self):
        self.existing_mapping = {}

    def initalize_contact_id_mapping(self):
        self.contact_id_mapping = {}
        for contact in Contact.query:
            former_id = contact.former_contact_id
            self.contact_id_mapping[former_id] = contact.contact_id

    def get_internal_obj(self, row):
        """Returns the related existing objects depending on
        the current row.
        """
        raise NotImplementedError()

    def get_remote_object(self, row):
        """Creates and returns a new object (without adding it
        to the db) instance with the given attributes in the row.
        """
        raise NotImplementedError()

    def add_object(self, obj):
        """Adds an object to the db
        """
        self.db_session.add(obj)
        self.stats['added'] += 1

    def update_object(self, source_obj, target_obj):
        """Updates the target_obj with the data of the
        source_obj.
        """
        updated = False
        for key in self.keys:
            if getattr(source_obj, key) == getattr(target_obj, key):
                continue

            setattr(target_obj, key, getattr(source_obj, key))
            updated = True

        if updated:
            self.stats['updated'] += 1
        else:
            self.stats['no_change'] += 1

        return updated

    def reset_statistic(self):
        self.stats = {'updated': 0, 'no_change': 0, 'added': 0, 'total': 0}

    def log_statistic(self):
        skipped = (self.stats.get('total') - self.stats.get('added')
                   - self.stats.get('updated') - self.stats.get('no_change'))

        logger.info("STATISTICS")
        logger.info("Total: {}".format(self.stats.get('total')))
        logger.info("Added: {}".format(self.stats.get('added')))
        logger.info("Updated: {}".format(self.stats.get('updated')))
        logger.info(
            "Updated - no change: {}".format(self.stats.get('no_change')))
        logger.info("Skipped: {}".format(skipped))

    def to_unicode(self, value):
        if value and not isinstance(value, unicode):
            return value.decode('utf-8')

        return value


class OrganizationSyncer(ObjectSyncer):

    type_name = "Organizations"

    keys = ['name', 'is_active']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for organization in Organization.query:
            self.existing_mapping[organization.former_contact_id] = organization

    def get_internal_obj(self, row):
        return self.existing_mapping.get(row.former_contact_id)

    def get_remote_object(self, row):
        return Organization(
            name=self.to_unicode(row.name),
            former_contact_id=row.former_contact_id,
            is_active=row.is_active)


class PersonSyncer(ObjectSyncer):

    type_name = "Persons"

    keys = ['salutation', 'academic_title',
            'firstname', 'lastname', 'is_active']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for person in Person.query:
            self.existing_mapping[person.former_contact_id] = person

    def get_internal_obj(self, row):
        return self.existing_mapping.get(row.former_contact_id)

    def get_remote_object(self, row):
        return Person(salutation=self.to_unicode(row.salutation),
                      academic_title=self.to_unicode(row.title),
                      firstname=self.to_unicode(row.firstname),
                      lastname=self.to_unicode(row.lastname),
                      former_contact_id=row.former_contact_id,
                      is_active=row.is_active)


class MailSyncer(ObjectSyncer):

    type_name = "Mails"

    keys = ['address', 'label']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for mail in MailAddress.query:
            key = u'{}:{}'.format(mail.label, mail.contact.former_contact_id)
            self.existing_mapping[key] = mail

    def get_internal_obj(self, row):
        key = u'{}:{}'.format(self.to_unicode(row.label), row.former_contact_id)
        return self.existing_mapping.get(key)

    def get_remote_object(self, row):
        contact = Contact.query.get_by_former_contact_id(row.former_contact_id)

        if not contact:
            return None

        return MailAddress(
            contact_id=contact.contact_id,
            address=self.to_unicode(row.address),
            label=self.to_unicode(row.label))


class UrlSyncer(ObjectSyncer):

    type_name = "Urls"

    keys = ['url', 'label']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for url in URL.query:
            key = u'{}:{}'.format(url.label, url.contact.former_contact_id)
            self.existing_mapping[key] = url

    def get_internal_obj(self, row):
        key = u'{}:{}'.format(self.to_unicode(row.label), row.former_contact_id)
        return self.existing_mapping.get(key)

    def get_remote_object(self, row):
        contact = Contact.query.get_by_former_contact_id(row.former_contact_id)

        if not contact:
            return None

        return URL(contact_id=contact.contact_id,
                   url=self.save_url(self.to_unicode(row.url)),
                   label=self.to_unicode(row.label))

    def save_url(self, url):
        if not urlparse(url).scheme:
            return u'http://{}'.format(url)

        return url


class PhoneNumberSyncer(ObjectSyncer):

    type_name = "Phonenumbers"

    keys = ['phone_number', 'label']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for phone in PhoneNumber.query:
            key = u'{}:{}'.format(phone.label, phone.contact.former_contact_id)
            self.existing_mapping[key] = phone

    def get_internal_obj(self, row):
        key = u'{}:{}'.format(self.to_unicode(row.label), row.former_contact_id)
        return self.existing_mapping.get(key)

    def get_remote_object(self, row):
        contact = Contact.query.get_by_former_contact_id(row.former_contact_id)

        if not contact:
            return None

        return PhoneNumber(
            contact_id=contact.contact_id,
            phone_number=self.to_unicode(row.phone_number),
            label=self.to_unicode(row.label))


class AddressSyncer(ObjectSyncer):

    type_name = "Addresses"

    keys = ['label', 'street', 'zip_code', 'city', 'country']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for address in Address.query:
            key = u'{}:{}'.format(address.label, address.contact.former_contact_id)
            self.existing_mapping[key] = address

    def get_internal_obj(self, row):
        key = u'{}:{}'.format(self.to_unicode(row.label), row.former_contact_id)
        return self.existing_mapping.get(key)

    def get_remote_object(self, row):
        contact = Contact.query.get_by_former_contact_id(row.former_contact_id)

        if not contact:
            return None

        return Address(
            contact_id=contact.contact_id,
            label=self.to_unicode(row.label),
            street=self.to_unicode(row.street),
            zip_code=self.to_unicode(row.zip_code),
            city=self.to_unicode(row.city),
            country=self.to_unicode(row.country))


class OrgRoleSyncer(ObjectSyncer):

    type_name = "OrgRoles"

    keys = ['function']

    def initalize_existing_mapping(self):
        self.existing_mapping = {}
        for org_role in OrgRole.query:
            key = u'{}:{}'.format(
                org_role.person.former_contact_id,
                org_role.organization.former_contact_id)

            self.existing_mapping[key] = org_role

    def get_internal_obj(self, row):
        key = u'{}:{}'.format(row.person_id, row.organisation_id)
        return self.existing_mapping.get(key)

    def get_remote_object(self, row):
        person = Contact.query.get_by_former_contact_id(row.person_id)

        organization = Contact.query.get_by_former_contact_id(
            row.organisation_id)

        if not person or not organization:
            return None

        return OrgRole(
            person_id=person.contact_id,
            organization_id=organization.contact_id,
            function=self.to_unicode(row.function))
