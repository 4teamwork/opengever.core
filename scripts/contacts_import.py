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
from opengever.base.model import create_session
from opengever.contact.models import Address
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


def main(app, argv=sys.argv[1:]):
    options, args = parser.parse_args()

    path = options.path if options.path else None
    if not path:
        print_parser_error('Please specify the "path" with "-p path/to/csv"\n')

    object_type = options.object_type if options.object_type else None
    if not object_type:
        print_parser_error(
            'Please specify a "object_type" with "-t object_type"\n')

    try:
        importer.run_import(path, object_type)
    except BadPathException:
        print_parser_error(
            'At "{}" is no file."\n'
            'Please specify a valid path to a csv-file.'.format(path))
    except BadTypeException:
        print_parser_error(
            "The type '{}'' is not allowed to import. Please use one of the "
            "following types: {}".format(
                object_type, ', '.join(importer.allowed_object_types)))


def print_parser_error(msg):
    parser.print_help()
    parser.error(msg)


class CSVContactImporter(object):
    """Imports contacts and its related tables
    """

    allowed_object_types = ['person']

    def __init__(self):
        self.db_session = create_session()

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

    def reader(self, path, rows, check_header_row=True):
        with open(path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, rows)
            for i, row in enumerate(reader):
                if check_header_row and i <= 0:
                    self.validate_header(rows, row.values())
                yield row

    def validate_header(self, rows, header_rows):
        if rows == header_rows:
            return True

        raise BadCSVFormatException(
            "The csv-format is broken.\n"
            "We excpect the following header rows: {}\n"
            "but the csv has the following rows definded: {}\n".format(
                rows, header_rows)
            )

    def import_person(self, path):
        LOG.info("Start importing contacts...")

        rows = ['title', 'firstname', 'lastname', 'contact_id', 'salutation']

        for row in self.reader(path, rows):
            person = Person(salutation=row.get('salutation'),
                            academic_title=row.get('title'),
                            firstname=row.get('firstname'),
                            lastname=row.get('lastname'))

            self.db_session.add(person)


importer = CSVContactImporter()
parser = OptionParser()

parser.add_option("-p", "--path", dest="path",
                  help="REQUIRED: Specify the path to a csv-file which "
                       "you want to import.")

parser.add_option("-t", "--object_type", dest="object_type",
                  help="REQUIRED: Set the object type name you want to create.\n"
                       "Available types: {}".format(
                           ', '.join(importer.allowed_object_types)))

parser.add_option("-c", "--config", dest="config",
                  help="Zope-Config (do not use this)")


if __name__ == '__main__':
    main(app, sys.argv[1:])
