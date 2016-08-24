"""
Script to sync or import contacts and its related tables (i.e. mails, numbers...)
from csv.

To run the import just type in the following command:

    bin/instance run ./scripts/contact_syncer.py -p /path/to/contact.csv -t [person, url, mail...]

For help-information type in the following:

    bin/instance run ./scripts/contact_syncer.py -h

"""
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
import argparse
import csv
import logging
import sys
import transaction


# Set global logger to info - this is necessary for the log-output with
# bin/instance run.
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

LOG = logging.getLogger('contacts-import')


class BadTypeException(AttributeError):
    pass


class BadCSVFormatException(AttributeError):
    pass


class ObjectSyncer(object):
    """Use the objectsyncer to sync a sql-table with a csv-file.
    """
    db_session = None

    # Key = csv-row
    # Value = sql-row
    rows_mapping = OrderedDict()

    # For logging
    type_name = ""

    stat_updated = 0
    stat_added = 0
    stat_removed = 0
    stat_total = 0

    file_ = None

    sql_object = None
    csv_object = None

    def __init__(self, file_):
        self.db_session = create_session()
        self.file_ = file_
        self.update_rows_mapping()

    def __call__(self):
        LOG.info("Syncing {}...".format(self.type_name))
        self.reset_statistic()

        for row in self.reader(self.file_, self.rows_mapping.keys()):
            self.stat_total += 1

            sql_object = self.get_sql_obj(row)
            csv_object = self.get_csv_obj(row)

            if not csv_object:
                continue

            if sql_object:
                self.update_object(csv_object, sql_object)
            else:
                self.add_object(csv_object)

        self.handle_objects_to_remove()

        LOG.info("Syncing of {} succeeded".format(self.type_name))
        self.log_statistic()

        transaction.commit()

    def reader(self, file_, rows):
        self.validate_header(file_, rows)
        for row in csv.DictReader(file_, rows):
            yield row

    def add_object(self, obj):
        self.db_session.add(obj)
        self.stat_added += 1

    def update_object(self, source_obj, target_obj):
        updated = False
        for row in self.rows_mapping.values():
            if getattr(source_obj, row) == getattr(target_obj, row):
                continue

            setattr(target_obj, row, getattr(source_obj, row))
            updated = True

        if updated:
            self.stat_updated += 1

    def update_rows_mapping(self):
        raise NotImplementedError()

    def handle_objects_to_remove(self):
        raise NotImplementedError()

    def get_sql_obj(self, csv_row):
        raise NotImplementedError()

    def get_csv_obj(self, csv_row):
        raise NotImplementedError()

    def validate_header(self, file_, rows):
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

    def reset_statistic(self):
        self.stat_added = 0
        self.stat_updated = 0
        self.stat_deleted = 0
        self.stat_total = 0

    def log_statistic(self):
        skipped = self.stat_total - self.stat_added - self.stat_updated - self.stat_removed

        LOG.info(
            "STATISTICS\n"
            "----------\n\n"
            "Total: {}\n"
            "Added: {}\n"
            "Updated: {}\n"
            "Removed: {}\n"
            "Skipped: {}\n".format(
                self.stat_total, self.stat_added, self.stat_updated, self.stat_removed, skipped))

    def decode_text(self, text):
        if not text:
            return text

        return text.decode('utf-8')


class OrganizationSyncer(ObjectSyncer):

    type_name = "Organizations"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'former_contact_id'
        self.rows_mapping['name'] = 'name'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return Organization.query.filter(
            Organization.former_contact_id == csv_row.get('contact_id')).first()

    def get_csv_obj(self, csv_row):
        return Organization(
            name=self.decode_text(csv_row.get('name')),
            former_contact_id=int(self.decode_text(csv_row.get('contact_id'))))


class PersonSyncer(ObjectSyncer):

    type_name = "Persons"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'former_contact_id'
        self.rows_mapping['salutation'] = 'salutation'
        self.rows_mapping['title'] = 'academic_title'
        self.rows_mapping['firstname'] = 'firstname'
        self.rows_mapping['lastname'] = 'lastname'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return Person.query.filter(
            Person.former_contact_id == csv_row.get('contact_id')).first()

    def get_csv_obj(self, csv_row):
        return Person(salutation=self.decode_text(csv_row.get('salutation')),
                      academic_title=self.decode_text(csv_row.get('title')),
                      firstname=self.decode_text(csv_row.get('firstname')),
                      lastname=self.decode_text(csv_row.get('lastname')),
                      former_contact_id=int(self.decode_text(csv_row.get('contact_id'))))


class MailSyncer(ObjectSyncer):

    type_name = "Mails"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['mail_address'] = 'address'
        self.rows_mapping['label'] = 'label'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return None

    def get_csv_obj(self, csv_row):
        contact_id = Contact.query.get_by_former_contact_id(
            csv_row.get('contact_id'))

        if not contact_id:
            return None

        return MailAddress(
            contact_id=contact_id,
            address=self.decode_text(csv_row.get('mail_address')),
            label=self.decode_text(csv_row.get('label')))


class UrlSyncer(ObjectSyncer):

    type_name = "Urls"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['url'] = 'url'
        self.rows_mapping['label'] = 'label'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return None

    def get_csv_obj(self, csv_row):
        contact_id = Contact.query.get_by_former_contact_id(
            csv_row.get('contact_id'))

        if not contact_id:
            return None

        return URL(
            contact_id=contact_id,
            url=self.decode_text(csv_row.get('url')),
            label=self.decode_text(csv_row.get('label')))


class PhoneNumberSyncer(ObjectSyncer):

    type_name = "Phonenumbers"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['number'] = 'phone_number'
        self.rows_mapping['label'] = 'label'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return None

    def get_csv_obj(self, csv_row):
        contact_id = Contact.query.get_by_former_contact_id(
            csv_row.get('contact_id'))

        if not contact_id:
            return None

        return PhoneNumber(
            contact_id=contact_id,
            phone_number=self.decode_text(csv_row.get('number')),
            label=self.decode_text(csv_row.get('label')))


class AddressSyncer(ObjectSyncer):

    type_name = "Addresses"

    def update_rows_mapping(self):
        self.rows_mapping['contact_id'] = 'contact_id'
        self.rows_mapping['label'] = 'label'
        self.rows_mapping['street'] = 'street'
        self.rows_mapping['zip'] = 'zip_code'
        self.rows_mapping['city'] = 'city'

        # HINT: This field does not exists on sql and will be ignored
        self.rows_mapping['country'] = 'country'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return None

    def get_csv_obj(self, csv_row):
        contact_id = Contact.query.get_by_former_contact_id(
            csv_row.get('contact_id'))

        if not contact_id:
            return None

        return Address(
            contact_id=contact_id,
            label=self.decode_text(csv_row.get('label')),
            street=self.decode_text(csv_row.get('street')),
            zip_code=self.decode_text(csv_row.get('zip')),
            city=self.decode_text(csv_row.get('city')),)


class OrgRoleSyncer(ObjectSyncer):

    type_name = "OrgRoles"

    def update_rows_mapping(self):
        self.rows_mapping['person_id'] = 'person_id'
        self.rows_mapping['organisation_id'] = 'organization_id'
        self.rows_mapping['function'] = 'function'

    def handle_objects_to_remove(self):
        pass

    def get_sql_obj(self, csv_row):
        return None

    def get_csv_obj(self, csv_row):
        person_id = Contact.query.get_by_former_contact_id(
            csv_row.get('person_id'))

        organization_id = Contact.query.get_by_former_contact_id(
            csv_row.get('organisation_id'))

        if not person_id or not organization_id:
            return None

        return OrgRole(
            person_id=person_id,
            organization_id=organization_id,
            function=self.decode_text(csv_row.get('function')))


class CSVContactImporter(object):
    """Object to handle the bin/instance run parameters and
    run the correct sync-objects.
    """

    import_types = {
        'organization': OrganizationSyncer,
        'person': PersonSyncer,
        'mail': MailSyncer,
        'url': UrlSyncer,
        'phonenumber': PhoneNumberSyncer,
        'address': AddressSyncer,
        'orgrole': OrgRoleSyncer,
    }

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-p", "--path", dest="file_", required=True,
            type=argparse.FileType('r+'),
            help="Specify the path to a csv-file which "
                 "you want to import.")

        self.parser.add_argument(
            "-t", "--object_type", dest="object_type", required=True,
            choices=self.import_types.keys(),
            help="Set the object type name you want to create.\n"
                 "Available types: {}".format(
                     ', '.join(self.import_types.keys())))

        self.parser.add_argument(
            "-c", "--config", dest="config",
            help="Zope-Config (do not use this)")

    def __call__(self, app, argv=sys.argv[1:]):
        options = self.parser.parse_args()
        self.import_types.get(options.object_type)(options.file_)()


if __name__ == '__main__':
    CSVContactImporter()(app, sys.argv[1:])
