"""
Script to sync or import contacts and its related tables (i.e. mails, numbers...)
from csv.

To run the import just type in the following command:

    bin/instance run ./scripts/contact_syncer.py -p /path/to/contact.csv -t [person, url, mail...]

For help-information type in the following:

    bin/instance run ./scripts/contact_syncer.py -h

"""
from opengever.contact import syncer
import argparse
import logging
import sys


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


class CSVContactImporter(object):
    """Object to handle the bin/instance run parameters and
    run the correct sync-objects.
    """

    import_types = {
        'organization': syncer.OrganizationSyncer,
        'person': syncer.PersonSyncer,
        'mail': syncer.MailSyncer,
        'url': syncer.UrlSyncer,
        'phonenumber': syncer.PhoneNumberSyncer,
        'address': syncer.AddressSyncer,
        'orgrole': syncer.OrgRoleSyncer,
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
