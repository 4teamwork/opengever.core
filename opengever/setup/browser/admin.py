from AccessControl.SecurityInfo import ClassSecurityInformation
from datetime import datetime
from opengever.ogds.base.utils import create_session
from opengever.setup.deploy import GeverDeployment
from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from Products.CMFPlone.browser.admin import AddPloneSite
from zope.component import getUtility
from zope.publisher.browser import BrowserView
import App.config
import logging
import os
import traceback


LOG = logging.getLogger('opengever.setup')


class ResponseLogger(object):

    security = ClassSecurityInformation()

    def __init__(self, response):
        self.response = response
        self.handler = None
        self.formatter = None

    def __enter__(self):
        self.handler = logging.StreamHandler(self)
        self.formatter = logging.root.handlers[-1].formatter
        self.handler.setFormatter(self.formatter)
        logging.root.addHandler(self.handler)

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            LOG.error('FAILED')
            traceback.print_exception(exc_type, exc_value, tb, None, self)

        logging.root.removeHandler(self.handler)

    security.declarePrivate('write')
    def write(self, line):
        if isinstance(line, unicode):
            line = line.encode('utf8')

        self.response.write(line)
        self.response.flush()

    security.declarePrivate('writelines')
    def writelines(self, lines):
        for line in lines:
            self.write(line)


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
        return '/++resource++adddeployment.js?x={}'.format(datetime.now())

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
        return engine.url

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
            db_info = "{} ({}): {} @{}".format(
                section_type, backend_type, user, dsn)
        else:
            # blobstorage
            db_info = section_type
        return db_info


class CreateDeployment(BrowserView):

    security = ClassSecurityInformation()

    def __call__(self):
        self.form = self.request.form
        self.db_session = create_session()

        policy_id = self.form['policy']
        deployment_registry = getUtility(IDeploymentConfigurationRegistry)
        self.config = deployment_registry.get_deployment(policy_id)
        return self.install_with_ajax_stream()

    def _install(self):
        """Installs the selected gever deployment.
        """
        is_development_setup = self.form.get('dev_mode', False)
        if is_development_setup:
            self.request['unit_creation_dev_mode'] = True

        deployment = GeverDeployment(
            self.context, self.config, self.db_session,
            is_development_setup=is_development_setup,
            has_purge_sql=self.form.get('purge_sql', False),
            ldap_profile=self.form.get('ldap', None),
            has_ldap_user_import=self.form.get('import_users', False))
        deployment.create()
        return deployment

    security.declarePrivate('install_with_ajax_stream')
    def install_with_ajax_stream(self):
        """Installs the selected gever deployment and streams the log into
        the HTTP response.

        Furthermore contains hackish javascript to scroll to end of output and
        display a link to the installed plone-site once the installation has
        finished.

        """
        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'text/html')
        response.setHeader('Transfer-Encoding', 'chunked')
        response.write('<html>')
        response.write('<head>')
        response.write(
            '<script type="text/javascript" language="javascript" '
            '        src="/++resource++opengever.setup-jquery.min.js">'
            '</script>'
        )
        response.write('</head>')
        response.write('<body>')
        response.write('  ' * getattr(response, 'http_chunk_size', 100))
        response.write('<pre>')

        with ResponseLogger(self.request.RESPONSE):
            deployment = self._install()

        site_url = deployment.site.absolute_url()
        site_title = self.config['title']

        response.write(
            '<script type="text/javascript">'
            '    var iframe = $("#deploy-output", window.parent.document);'
            '    iframe.contents().scrollTop(iframe.contents().height());'
            '    $("#setup-completed a", window.parent.document)'
            '        .attr("href", "{}")'
            '        .html("Open deployment {}");'
            '    $("#setup-completed", window.parent.document).show();'
            '</script>'.format(site_url, site_title)
        )

        response.write('</pre>')
        response.write('</body>')
        response.write('</html>')
