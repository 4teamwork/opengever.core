from collections import OrderedDict
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
import csv
import logging
import transaction


LOG = logging.getLogger('contacts-import')


class BadCSVFormatException(AttributeError):
    pass


class FileReader(object):
    """ Contextmanager: Reads an open from beginning
    and put the seek-pointer back to 0 after reading
    """
    def __init__(self, file_):
        self.file_ = file_

    def __enter__(self):
        self.file_.seek(0)
        return self.file_

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_.seek(0)


class ObjectSyncerProgressLogger(ProgressLogger):

    def __init__(self, message, iterable, length, logger=None,
                 timeout=5):

        self.logger = logger or logging.getLogger('contactsyncer')
        self.message = message
        self.iterable = iterable

        self.timeout = timeout
        self._timestamp = None
        self._counter = 0

        self.length = length


class ObjectSyncer(object):
    """Use the objectsyncer to sync a sql-table with a file.
    """
    db_session = None

    rows_mapping = OrderedDict()  # key = file-row, value = sql-row

    # For logging
    type_name = ""

    stat_updated = 0
    stat_added = 0
    stat_total = 0

    total_items = 0

    file_ = None

    internal_object = None
    remote_object = None

    def __init__(self, file_):
        self.db_session = create_session()
        self.file_ = file_
        self.update_rows_mapping()
        self.total_items = self.count_total_items()

    def __call__(self):
        """Starts the sync-process
        """
        LOG.info("Syncing {}...".format(self.type_name))
        self.reset_statistic()

        for row in self.reader():
            self.stat_total += 1

            internal_object = self.get_internal_obj(row)
            remote_object = self.get_remote_object(row)

            if not remote_object:
                continue

            if internal_object:
                self.update_object(
                    self.rows_mapping, remote_object, internal_object)
            else:
                self.add_object(remote_object)

        LOG.info("Syncing of {} succeeded".format(self.type_name))
        self.log_statistic()

        transaction.commit()

    def update_rows_mapping(self):
        """This function will be called in the init of the class.

        Use it to update the rows_mapping dict.

        i.e.:

        self.rows_mapping['name'] = 'name'
        """
        pass

    def reader(self):
        """Reads the file and returns each row as a dict.
        """
        with FileReader(self.file_) as file_:
            iterable = ObjectSyncerProgressLogger(
                "Syncing {}".format(self.type_name),
                file_, self.total_items)

            for row in iterable:
                yield row

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
        self.stat_added += 1

    def update_object(self, mapping, source_obj, target_obj):
        """Updates the target_obj with the data of the
        source_obj.

        It compares the fields defined in the rows_mapping
        and only updates this fields.
        """
        updated = False
        for row in mapping.values():
            if getattr(source_obj, row) == getattr(target_obj, row):
                continue

            setattr(target_obj, row, getattr(source_obj, row))
            updated = True

        if updated:
            self.stat_updated += 1

        return updated

    def reset_statistic(self):
        self.stat_added = 0
        self.stat_updated = 0
        self.stat_total = 0

    def count_total_items(self, skip_header_row=True):
        with FileReader(self.file_) as file_:
            for i, line in enumerate(file_):
                pass

        return i if skip_header_row else i + 1

    def log_statistic(self):
        skipped = self.stat_total - self.stat_added - self.stat_updated

        LOG.info(
            "STATISTICS\n"
            "----------\n\n"
            "Total: {}\n"
            "Added: {}\n"
            "Updated: {}\n"
            "Skipped: {}\n".format(
                self.stat_total, self.stat_added, self.stat_updated, skipped))

    def decode_text(self, text):
        if not text:
            return text

        return text.decode('utf-8')


class CSVObjectSyncer(ObjectSyncer):

    def reader(self):
        rows = self.rows_mapping.keys()
        with FileReader(self.file_) as file_:
            self._validate_header(file_, rows)

            iterable = ObjectSyncerProgressLogger(
                "Syncing {}".format(self.type_name),
                csv.DictReader(file_, rows),
                self.total_items)

            for row in iterable:
                yield row

    def _validate_header(self, file_, rows):
        reader = csv.reader(file_)
        header_rows = reader.next()

        if rows == header_rows:
            return True

        raise BadCSVFormatException(
            "The csv-format is broken.\n"
            "We excpect the following header rows: {}\n"
            "but the csv has the following rows definded: {}\n".format(
                rows, header_rows)
            )


class OrganizationSyncer(CSVObjectSyncer):

    type_name = "Organizations"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'former_contact_id'
        self.rows_mapping['name'] = 'name'

    def get_internal_obj(self, row):
        return Organization.query.filter(
            Organization.former_contact_id == row.get('contact_id')).first()

    def get_remote_object(self, row):
        return Organization(
            name=self.decode_text(row.get('name')),
            former_contact_id=int(self.decode_text(row.get('contact_id'))))


class PersonSyncer(CSVObjectSyncer):

    type_name = "Persons"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'former_contact_id'
        self.rows_mapping['salutation'] = 'salutation'
        self.rows_mapping['title'] = 'academic_title'
        self.rows_mapping['firstname'] = 'firstname'
        self.rows_mapping['lastname'] = 'lastname'

    def get_internal_obj(self, row):
        return Person.query.filter(
            Person.former_contact_id == row.get('contact_id')).first()

    def get_remote_object(self, row):
        return Person(salutation=self.decode_text(row.get('salutation')),
                      academic_title=self.decode_text(row.get('title')),
                      firstname=self.decode_text(row.get('firstname')),
                      lastname=self.decode_text(row.get('lastname')),
                      former_contact_id=int(self.decode_text(row.get('contact_id'))))


class MailSyncer(CSVObjectSyncer):

    type_name = "Mails"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['mail_address'] = 'address'
        self.rows_mapping['label'] = 'label'

    def get_internal_obj(self, row):
        return None

    def get_remote_object(self, row):
        contact_id = Contact.query.get_by_former_contact_id(
            row.get('contact_id'))

        if not contact_id:
            return None

        return MailAddress(
            contact_id=contact_id,
            address=self.decode_text(row.get('mail_address')),
            label=self.decode_text(row.get('label')))


class UrlSyncer(CSVObjectSyncer):

    type_name = "Urls"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['url'] = 'url'
        self.rows_mapping['label'] = 'label'

    def get_internal_obj(self, row):
        return None

    def get_remote_object(self, row):
        contact_id = Contact.query.get_by_former_contact_id(
            row.get('contact_id'))

        if not contact_id:
            return None

        return URL(
            contact_id=contact_id,
            url=self.decode_text(row.get('url')),
            label=self.decode_text(row.get('label')))


class PhoneNumberSyncer(CSVObjectSyncer):

    type_name = "Phonenumbers"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['number'] = 'phone_number'
        self.rows_mapping['label'] = 'label'

    def get_internal_obj(self, row):
        return None

    def get_remote_object(self, row):
        contact_id = Contact.query.get_by_former_contact_id(
            row.get('contact_id'))

        if not contact_id:
            return None

        return PhoneNumber(
            contact_id=contact_id,
            phone_number=self.decode_text(row.get('number')),
            label=self.decode_text(row.get('label')))


class AddressSyncer(CSVObjectSyncer):

    type_name = "Addresses"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['label'] = 'label'
        self.rows_mapping['street'] = 'street'
        self.rows_mapping['zip'] = 'zip_code'
        self.rows_mapping['city'] = 'city'

        # HINT: This field does not exists on sql and will be ignored
        self.rows_mapping['country'] = 'country'

    def get_internal_obj(self, row):
        return None

    def get_remote_object(self, row):
        contact_id = Contact.query.get_by_former_contact_id(
            row.get('contact_id'))

        if not contact_id:
            return None

        return Address(
            contact_id=contact_id,
            label=self.decode_text(row.get('label')),
            street=self.decode_text(row.get('street')),
            zip_code=self.decode_text(row.get('zip')),
            city=self.decode_text(row.get('city')),)


class OrgRoleSyncer(CSVObjectSyncer):

    type_name = "OrgRoles"

    def update_rows_mapping(self):
        self.rows_mapping['person_id'] = 'person_id'
        self.rows_mapping['organisation_id'] = 'organization_id'
        self.rows_mapping['function'] = 'function'

    def get_internal_obj(self, row):
        return None

    def get_remote_object(self, row):
        person_id = Contact.query.get_by_former_contact_id(
            row.get('person_id'))

        organization_id = Contact.query.get_by_former_contact_id(
            row.get('organisation_id'))

        if not person_id or not organization_id:
            return None

        return OrgRole(
            person_id=person_id,
            organization_id=organization_id,
            function=self.decode_text(row.get('function')))
