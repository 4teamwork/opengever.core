from AccessControl.SecurityManagement import newSecurityManager
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.model import create_session
from opengever.bundle.config.importer import ConfigImporter
from opengever.bundle.importer import BundleImporter
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.setup.deploy import GeverDeployment
from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import IDuringSetup
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import getUtility
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
import argparse
import codecs
import json
import logging
import os.path
import sys
import transaction


logger = logging.getLogger('opengever.setup')


def setup(app, args):
    parser = argparse.ArgumentParser(description="Setup a new GEVER deployment")
    parser.add_argument(
        '--profile',
        help='Name of the deployment profile',
        default='Policyless Deployment',
    )
    parser.add_argument(
        '--user',
        help='Name of the user used for creating the deployment',
        default='zopemaster',
    )
    parser.add_argument(
        '--purge-ogds', action='store_true',
        help="Purge OGDS before creating new deployment",
    )
    parser.add_argument(
        '--purge-solr', action='store_true',
        help="Purge Solr before creating new deployment",
    )
    parser.add_argument(
        '--purge-site', action='store_true',
        help="Purge Plone site before creating new deployment",
    )
    parser.add_argument(
        '--skip-ogds-sync', action='store_true',
        help="Do not sync OGDS after creating deployment",
    )
    parser.add_argument(
        '--bundle-path',
        help='Path to an OGG bundle to import after creating deployment',
        default='/oggbundle',
    )

    # If run with plone.recipe.zope2instance we need to strip the first 2 args
    if sys.argv[0] != 'setup':
        args = args[2:]
    options = parser.parse_args(args)

    setup_logging()

    for key, item in app.items():
        if item.meta_type == 'Plone Site':
            if options.purge_site:
                del app[key]
                transaction.get().note('Deleted Plone site.')
                transaction.commit()
                logger.info('Purged existing Plone site.')
            else:
                logger.error('A Plone site already exists.')
                sys.exit(1)

    logger.info('Creating new deployment...')

    app = setup_request(app)
    request = app.REQUEST
    alsoProvides(request, IDisableCSRFProtection)
    alsoProvides(request, IDuringSetup)

    deployment_registry = getUtility(IDeploymentConfigurationRegistry)
    config = deployment_registry.get_deployment(options.profile)

    become_user(app, options.user)

    transaction.begin()
    ogds_session = create_session()
    deployment = GeverDeployment(
        app, config, ogds_session,
        has_purge_sql=options.purge_ogds,
        has_purge_solr=options.purge_solr,
    )
    deployment.create()
    transaction.get().note('Created new deployment.')
    transaction.commit()
    logger.info('Created new deployment with site id: %s.', deployment.site)

    if not options.skip_ogds_sync:
        logger.info('Syncing OGDS...')
        sync_ogds(
            deployment.site,
            update_remote_timestamps=False,
            disable_logfile=True,
        )

    if os.path.exists(options.bundle_path):
        import_bundle(deployment.site, options.bundle_path)

    logger.info('Setup finished.')


def import_bundle(site, bundle_path):
    logger.info('Importing OGG bundle...')
    alsoProvides(site.REQUEST, IOpengeverBaseLayer)

    transaction.get().note('Bundle imported.')
    config_path = os.path.join(bundle_path, 'configuration.json')
    if os.path.exists(config_path):
        with codecs.open(config_path, 'r', 'utf-8-sig') as json_file:
            data = json.load(json_file)
        importer = ConfigImporter(data)
        importer.run()
    else:
        logger.error('configuration.json required for initital bundle import.')
        sys.exit(1)

    importer = BundleImporter(
        site,
        bundle_path,
        disable_ldap=False,
        create_guid_index=True,
        no_intermediate_commits=True,
        skip_report=True,
        create_initial_content=True,
        possibly_unpatch_collective_indexing=True,
        no_separate_connection_for_sequence_numbers=True,
        no_check_unique_principals=True,
    )
    importer.run()

    transaction.commit()
    logger.info('Bundle imported.')


def setup_request(app):
    # Delay import of the Testing module
    # Importing it before the database is opened, will result in opening a
    # DemoStorage database instead of the one from the config file.
    from Testing.makerequest import makerequest
    app = makerequest(app)
    setRequest(app.REQUEST)
    return app


def become_user(app, user):
    user = app.acl_users.getUser(user)
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)


def setup_logging():
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure output gets logged on console
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
