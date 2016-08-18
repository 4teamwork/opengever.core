"""
Script to import contacts and its related tables (i.e. mails, numbers...)
from csv.

To run the import you need to run the import by the following command:

    bin/instance run ./scripts/contacts_import.py -p /path/to/contact.csv -t contact

The script will automatically search for a table with the name of the file.
In your example case, it will import all the content of 'contact.csv' into
the 'contact'-table of the sql-db.

It will raise an error if the table does not exists.

For help-information type in the following:

    bin/instance run ./scripts/contacts_import.py -h

"""
# from ftw.bumblebee.interfaces import IBumblebeeConverter
# from opengever.core.debughelpers import get_first_plone_site
# from opengever.core.debughelpers import setup_plone
from collections import OrderedDict
from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import Contact
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from optparse import OptionParser
from path import Path
import csv
import logging
import sys
import transaction


# Set global logger to info - this is necessary for the log-outbut with
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


class BadPathException(AttributeError):
    pass


class BadCSVFormatException(AttributeError):
    pass


class CSVContactImporter(object):
    """Object to handle the bin/instance run parameters and
    run the correct sync-objects.
    """

    allowed_object_types = [
        'organization',
        'person',
        'mail',
    ]

    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option(
            "-p", "--path", dest="path",
            help="REQUIRED: Specify the path to a csv-file which "
                 "you want to import.")

        self.parser.add_option(
            "-t", "--object_type", dest="object_type",
            help="REQUIRED: Set the object type name you want to create.\n"
                 "Available types: {}".format(
                     ', '.join(self.allowed_object_types)))

        self.parser.add_option(
            "-c", "--config", dest="config",
            help="Zope-Config (do not use this)")

    def __call__(self, app, argv=sys.argv[1:]):
        options, args = self.parser.parse_args()

        path = options.path if options.path else None
        if not path:
            self.print_parser_error('Please specify the "path" with "-p path/to/csv"\n')

        object_type = options.object_type if options.object_type else None
        if not object_type:
            self.print_parser_error(
                'Please specify a "object_type" with "-t object_type"\n')

        try:
            self.run_import(path, object_type)
        except BadPathException:
            self.print_parser_error(
                'At "{}" is no file."\n'
                'Please specify a valid path to a csv-file.'.format(path))
        except BadTypeException:
            self.print_parser_error(
                "The type '{}'' is not allowed to import. Please use one of the "
                "following types: {}".format(
                    object_type, ', '.join(self.allowed_object_types)))

    def is_type_allowed(self, object_type):
        return object_type in self.allowed_object_types

    def is_valid_path(self, path):
        return path.isfile()

    def run_import(self, path, object_type):
        path = Path(path)
        if not self.is_valid_path(path):
            raise BadPathException()
        if not self.is_type_allowed(object_type):
            raise BadTypeException()

        getattr(self, 'import_{}'.format(object_type))(path)

    def import_person(self, path):
        PersonSyncer(path)()

    def import_mail(self, path):
        MailSyncer(path)()

    def import_organization(self, path):
        OrganizationSyncer(path)()

    def print_parser_error(self, msg):
        self.parser.print_help()
        self.parser.error(msg)


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

    csv_path = None

    sql_object = None
    csv_object = None

    def __init__(self, csv_path):
        self.db_session = create_session()
        self.csv_path = csv_path
        self.update_rows_mapping()

    def __call__(self):
        LOG.info("Syncing {}...".format(self.type_name))
        self.reset_statistic()

        for row in self.reader(self.csv_path, self.rows_mapping.keys()):
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

    def reader(self, path, rows):
        self.validate_header(rows)

        with open(path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, rows)
            for row in reader:
                if reader.line_num <= 1:
                    #skip header row
                    continue

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

    def validate_header(self, rows):
        with open(self.csv_path, 'rb') as csvfile:
            reader = csv.reader(csvfile)
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

    def get_contact_id_by_former_contact_id(self, former_contact_id):
        contact = Contact.query.filter(
            Contact.former_contact_id == former_contact_id).first()

        return contact.contact_id if contact else None


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
        contact_id = self.get_contact_id_by_former_contact_id(
            csv_row.get('contact_id'))

        if not contact_id:
            return None

        return MailAddress(
            contact_id=contact_id,
            address=self.decode_text(csv_row.get('mail_address')),
            label=self.decode_text(csv_row.get('label')))


if __name__ == '__main__':
    CSVContactImporter()(app, sys.argv[1:])
