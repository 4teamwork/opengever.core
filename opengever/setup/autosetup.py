from ftw.upgrade.interfaces import IExecutioner
from ftw.upgrade.interfaces import IUpgradeInformationGatherer
from opengever.base.model import create_session
from opengever.setup.deploy import GeverDeployment
from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import IDuringSetup
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest
from time import sleep
from ZODB.POSException import ConflictError
from zope.component import getAdapter
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.interface import alsoProvides
import logging
import os
import transaction


LOCK_KEY = 'openever.setup.autosetup-lock'

logger = logging.getLogger('opengever.setup.autosetup')


def autosetup(event):
    if not os.environ.get('OG_AUTOSETUP') == '1':
        return
    logger.info('Running autosetup...')
    conn = event.database.open()
    try:
        app = get_app(conn)
        if app is not None:
            if acquire_lock(conn):
                app = makerequest(app)
                site = get_or_create_site(app)
                if site is not None:
                    setSite(site)
                    install_upgrades(site)
            else:
                wait_until_unlocked(conn)
    except Exception:
        logger.exception('An exception occured during autosetup.')
    finally:
        setSite(None)
        transaction.abort()
        release_lock(conn)
        conn.close()


def get_app(conn):
    try:
        root = conn.root()
        app = root['Application']
    except KeyError:
        logger.info('Root not ready.')
        app = None
    return app


def acquire_lock(conn):
    root = conn.root()
    if LOCK_KEY not in root:
        root[LOCK_KEY] = True
        transaction.get().note('Acquired autosetup lock')
        try:
            transaction.commit()
        except ConflictError:
            logger.info('Could not acquire autosetup lock. Conflict error.')
            return False
        logger.info('Acquired autosetup lock.')
        return True
    else:
        logger.info('Could not acquire autosetup lock. Already locked.')
        return False


def release_lock(conn):
    transaction.begin()
    root = conn.root()
    if LOCK_KEY in root:
        del root[LOCK_KEY]
        transaction.get().note('Released autosetup lock')
        transaction.commit()
        logger.info('Released autosetup lock.')


def wait_until_unlocked(conn):
    delay = 5
    while True:
        transaction.begin()
        root = conn.root()
        if LOCK_KEY not in root:
            transaction.abort()
            logger.info('Autosetup finished.')
            return
        logger.info('Autosetup in progress. Waiting %s seconds...', delay)
        sleep(delay)
        delay = min(delay * 2, 300)


def get_or_create_site(app):
    sites = []
    for item in app.values():
        if item.meta_type == 'Plone Site':
            sites.append(item)

    if len(sites) == 1:
        logger.info('Found site: %s', sites[0])
        return sites[0]
    elif len(sites) > 1:
        logger.info('Multiple Plone Sites found. Skipping startup handler.')
        return None
    else:
        logger.info('No site found.')
        return create_site(app)


def create_site(app):
    if os.environ.get('OG_SKIP_SITE_CREATION'):
        return None

    logger.info('Creating site...')
    request = app.REQUEST
    alsoProvides(request, IDisableCSRFProtection)
    alsoProvides(request, IDuringSetup)
    deployment_registry = getUtility(IDeploymentConfigurationRegistry)
    config = deployment_registry.get_deployment('Policyless Deployment')

    transaction.begin()
    ogds_session = create_session()
    deployment = GeverDeployment(app, config, ogds_session)
    deployment.create()
    transaction.get().note('Created new site.')
    transaction.commit()
    logger.info('Created new site: %s.', deployment.site)

    os.environ['OG_SKIP_UPGRADES'] = '1'
    return deployment.site


def install_upgrades(site):
    if os.environ.get('OG_SKIP_UPGRADES'):
        return None

    propose_deferrable = os.environ.get('OG_SKIP_DEFERRABLE', '0').lower() not in [
        '1', 'true', 'yes', 'on']
    gstool = getToolByName(site, 'portal_setup')
    gatherer = IUpgradeInformationGatherer(gstool)
    profiles = gatherer.get_profiles(
        proposed_only=True, propose_deferrable=propose_deferrable)

    if profiles:
        logger.info('Installing upgrades...')
        transaction.begin()
        executioner = getAdapter(gstool, IExecutioner)
        executioner.install([
            (p['id'], [u['id'] for u in p['upgrades']]) for p in profiles
        ])
        transaction.get().note('Installed upgrades.')
        transaction.commit()
        logger.info('Finished installing upgrades.')
