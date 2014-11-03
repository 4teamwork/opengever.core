from datetime import datetime
from opengever.ogds.base.utils import create_session
from opengever.setup.deploy import GeverDeployment
from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from Products.CMFPlone.browser.admin import AddPloneSite
from zope.component import getUtility
from zope.publisher.browser import BrowserView
import App.config
import os


class SetupError(Exception):
    """An Error happened during OpenGever setup.
    """


class AddDeployment(AddPloneSite):

    def __call__(self):
        self.is_development_mode = os.environ.get('IS_DEVELOPMENT_MODE', False)
        return self.index()

    def javascript_src_url(self):
        """returns the url to the javascript. This makes it possible to
        change the URL in debug mode.

        """
        base_url = '/++resource++addclient.js'
        return base_url + '?x=' + str(datetime.now())

    def get_ldap_profiles(self):
        """Returns a list of (name, profile) of ldap GS profiles.
        """
        ldap_registry = getUtility(ILDAPConfigurationRegistry)
        return ldap_registry.list_ldaps()

    def get_deployment_profiles(self):
        deployment_registry = getUtility(IDeploymentConfigurationRegistry)
        return deployment_registry.list_deployments()

    def get_ogds_config(self):
        """Returns the DSN URL for the OGDS DB connection currently being
        used.
        """
        session = create_session()
        engine = session.bind
        return "%s" % engine.url

    def get_zodb_config(self):
        """Returns information about the ZODB configuration.
        """
        db_info = ""
        conf = App.config.getConfiguration()
        main_db = [db for db in conf.databases if db.name == 'main'][0]
        storage_cfg = main_db.config.storage.config
        section_type = storage_cfg.getSectionType()

        if section_type == 'relstorage':
            adapter_cfg = storage_cfg.adapter.config
            backend_type = adapter_cfg._matcher.type.name
            dsn = adapter_cfg.dsn
            user = adapter_cfg.user
            db_info = "%s (%s): %s @%s" % (
                section_type, backend_type, user, dsn)
        else:
            # blobstorage
            db_info = "%s" % section_type
        return db_info


class CreateDeployment(BrowserView):

    def __call__(self):
        form = self.request.form
        db_session = create_session()

        policy_id = form['policy']
        deployment_registry = getUtility(IDeploymentConfigurationRegistry)
        config = deployment_registry.get_deployment(policy_id)

        is_development_setup = form.get('dev_mode', False)
        if is_development_setup:
            self.request['unit_creation_dev_mode'] = True

        deployment = GeverDeployment(
            self.context, config, db_session,
            is_development_setup=is_development_setup,
            has_purge_sql=form.get('purge_sql', False),
            ldap_profile=form.get('ldap', None),
            has_ldap_user_import=form.get('import_users', False))
        deployment.create()
