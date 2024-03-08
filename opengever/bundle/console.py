# Avoid import error for Products.Archetypes.BaseBTreeFolder
from Products.Archetypes import atapi  # noqa # isort:skip
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.bundle.config.importer import ConfigImporter
from opengever.bundle.importer import BundleImporter
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from os.path import join as pjoin
from zope.interface import alsoProvides
import argparse
import codecs
import json
import logging
import os
import sys
import transaction


# BBB
from opengever.bundle.importer import add_guid_index  # noqa # isort:skip


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Import an OGGBundle')
    parser.add_argument('bundle_path',
                        help='Path to the .oggbundle directory')
    parser.add_argument('--no-intermediate-commits', action='store_true',
                        help="Don't to intermediate commits")
    parser.add_argument('--no-check-unique-principals', action='store_true',
                        help="Don't to check for OGDS principal name uniqueness")

    args = parser.parse_args(argv)
    return args


def import_oggbundle(app, args):
    """Handler for the 'bin/instance import' zopectl command.
    """
    setup_logging()

    # Discard the first three arguments, because they're not "actual" arguments
    # but cruft that we get because of the way bin/instance [zopectl_cmd]
    # scripts work.
    if sys.argv[0] != 'import':
        args = parse_args(sys.argv[3:])
    else:
        args = parse_args(args)

    log.info("Importing OGGBundle %s" % args.bundle_path)

    plone = setup_plone(get_first_plone_site(app))

    # mark request with GEVER layer
    alsoProvides(plone.REQUEST, IOpengeverBaseLayer)

    import_config_from_bundle(app, args)

    importer = BundleImporter(
        plone,
        args.bundle_path,
        disable_ldap=True,
        create_guid_index=True,
        no_intermediate_commits=args.no_intermediate_commits,
        possibly_unpatch_collective_indexing=True,
        no_separate_connection_for_sequence_numbers=True,
        no_check_unique_principals=args.no_check_unique_principals,
    )
    importer.run()

    log.info("Committing transaction...")
    transaction.get().note(
        "Finished import of OGGBundle %r" % args.bundle_path)
    transaction.commit()
    log.info("Done.")


def import_config_from_bundle(app, args):

    def _load_json(bundle_path, json_name):
        # TODO: Refactor bundle loader to extract this
        json_path = pjoin(bundle_path, json_name)
        log.info("Loading %s" % json_path)
        try:
            with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                data = json.load(json_file)
        except IOError as exc:
            log.info('%s: %s, skipping' % (json_name, exc.strerror))
            return None
        return data

    development_mode = bool(os.environ.get('IS_DEVELOPMENT_MODE'))
    json_data = _load_json(args.bundle_path, 'configuration.json')
    if json_data:
        importer = ConfigImporter(json_data)
        importer.run(development_mode=development_mode)


def setup_logging():
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure output gets logged on console
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    # Also write logs to a dedicated migration log in the working directory.
    file_handler = logging.FileHandler('migration.log')
    file_handler.setFormatter(stream_handler.formatter)
    file_handler.setLevel(logging.INFO)
    logging.root.addHandler(file_handler)
