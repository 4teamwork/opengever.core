from opengever.exportng.db import metadata
from opengever.exportng.sync import Syncer
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
import argparse
import logging
import sys


logger = logging.getLogger('opengever.exportng')


def exportng(app, args):
    parser = argparse.ArgumentParser(description="Export data")
    parser.add_argument(
        '--mapping',
        help='Name of the mapping file (Excel)',
        default='OGG-Mapping.xlsx',
    )
    parser.add_argument(
        '--drop-tables', '-D',
        help='Drop all tables',
        action='store_true',
    )
    parser.add_argument(
        '--site-path', '-s',
        help='Path to the Plone site.',
        default=None,
    )

    # If run with plone.recipe.zope2instance we need to strip the first 2 args
    if sys.argv[0] != 'exportng':
        args = args[2:]
    options = parser.parse_args(args)

    setup_logging()
    app = setup_request(app)
    site = get_site(app, options.site_path)
    setSite(site)

    # mapping = read_mapping(options.mapping)
    # create_or_reflect_tables(mapping, drop=options.drop_tables)
    metadata.reflect()
    if options.drop_tables:
        metadata.drop_all()
        metadata.clear()

    syncer = Syncer()
    syncer.create_tables()
    syncer.sync()


def setup_logging():
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure output gets logged on console
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logging.root.setLevel(logging.INFO)


def setup_request(app):
    # Delay import of the Testing module
    # Importing it before the database is opened, will result in opening a
    # DemoStorage database instead of the one from the config file.
    from Testing.makerequest import makerequest
    app = makerequest(app)
    setRequest(app.REQUEST)
    return app


def get_site(app, site_path):
    if site_path is not None:
        return app.unrestrictedTraverse(site_path)
    else:
        sites = []
        for item in app.values():
            if item.meta_type == 'Plone Site':
                sites.append(item)
        if len(sites) == 1:
            return sites[0]
        elif len(sites) > 1:
            logger.info('Multiple Plone site found.')
            sys.exit(1)
        else:
            logger.info('No Plone site found.')
            sys.exit(1)
