from collections import OrderedDict
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


class BadTypeException(AttributeError):
    pass


class BadCSVFormatException(AttributeError):
    pass


class ObjectSyncer(object):
    """Use the objectsyncer to sync a sql-table with a file.
    """
    db_session = None

    rows_mapping = OrderedDict()  # key = file-row, value = sql-row

    # For logging
    type_name = ""

    stat_updated = 0
    stat_added = 0
    stat_deleted = 0
    stat_total = 0

    file_ = None

    internal_object = None
    remote_object = None

    def __init__(self, file_):
        self.db_session = create_session()
        self.file_ = file_
        self.update_rows_mapping()

    def __call__(self):
        """Starts the sync-process
        """
        LOG.info("Syncing {}...".format(self.type_name))
        self.reset_statistic()

        for row in self.reader(self.file_, self.rows_mapping.keys()):
            self.stat_total += 1

            internal_object = self.get_internal_obj(row)
            remote_object = self.get_remote_object(row)

            if not remote_object:
                continue

            if internal_object:
                self.update_object(remote_object, internal_object)
            else:
                self.add_object(remote_object)

        self.remove_object()

        LOG.info("Syncing of {} succeeded".format(self.type_name))
        self.log_statistic()

        transaction.commit()

    def reader(self, file_, rows):
        """Reads the file and returns each row as a dict.
        """
        raise NotImplementedError

    def update_rows_mapping(self):
        """This function will be called in the init of the class.

        Use it to update the rows_mapping dict.

        i.e.:

        self.rows_mapping['name'] = 'name'
        """
        raise NotImplementedError()

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

    def remove_object(self, obj):
        """Removes an object from the db
        """
        self.db_session.delete(obj)
        self.stat_deleted += 1

    def add_object(self, obj):
        """Adds an object to the db
        """
        self.db_session.add(obj)
        self.stat_added += 1

    def update_object(self, source_obj, target_obj):
        """Updates the target_obj with the data of the
        source_obj.

        It compares the fields defined in the rows_mapping
        and only updates this fields.
        """
        updated = False
        for row in self.rows_mapping.values():
            if getattr(source_obj, row) == getattr(target_obj, row):
                continue

            setattr(target_obj, row, getattr(source_obj, row))
            updated = True

        if updated:
            self.stat_updated += 1

    def reset_statistic(self):
        self.stat_added = 0
        self.stat_updated = 0
        self.stat_deleted = 0
        self.stat_total = 0

    def log_statistic(self):
        skipped = self.stat_total - self.stat_added - self.stat_updated - self.stat_deleted

        LOG.info(
            "STATISTICS\n"
            "----------\n\n"
            "Total: {}\n"
            "Added: {}\n"
            "Updated: {}\n"
            "Removed: {}\n"
            "Skipped: {}\n".format(
                self.stat_total, self.stat_added, self.stat_updated, self.stat_deleted, skipped))

    def decode_text(self, text):
        if not text:
            return text

        return text.decode('utf-8')


class CSVObjectSyncer(ObjectSyncer):

    def reader(self, file_, rows):
        self._validate_header(file_, rows)
        for row in csv.DictReader(file_, rows):
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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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

    def remove_object(self):
        pass

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
