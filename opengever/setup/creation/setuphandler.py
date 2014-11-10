from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from plone import api
import os


UNIT_CREATION_FOLDER_NAME = 'unit_creation'
ADMIN_UNIT_FILENAME = 'admin_units.json'
ORG_UNIT_FILENAME = 'org_units.json'

LOCAL_ROLE_CONFIGURATION_FOLDER_NAME = 'local_role_configuration'

GEVER_CONTENT_FOLDER_NAME = 'opengever_content'

DEVELOP_USERS_GROUP = 'og_demo-ftw_users'

REPOSITORY_FILENAME = 'repository.xlsx'


class BaseSetupHandler(object):

    folder_name = None

    def __init__(self, setup):
        self.setup = setup
        self.path = os.path.join(setup._profile_path,
                                 self.folder_name).encode('utf-8')
        assert os.path.isdir(self.path)
        request = api.portal.get().REQUEST

        self.is_development_setup = request.get(
            'unit_creation_dev_mode', False)


def unit_creation(setup):
    """Create initial Org-Units and Admin-Units.
    """
    data = setup.isDirectory(UNIT_CREATION_FOLDER_NAME)
    if not data:
        return

    UnitCreation(setup).create_units()


class UnitCreation(BaseSetupHandler):

    folder_name = UNIT_CREATION_FOLDER_NAME

    def create_units(self):
        files = self.setup.listDirectory(self.path)

        if ADMIN_UNIT_FILENAME in files:
            self.create_admin_units(
                os.path.join(self.path, ADMIN_UNIT_FILENAME))

        if ORG_UNIT_FILENAME in files:
            self.create_org_units(
                os.path.join(self.path, ORG_UNIT_FILENAME))

    def create_admin_units(self, path):
        with open(path) as jsonfile:
            AdminUnitCreator(
                is_development=self.is_development_setup).run(jsonfile)

    def create_org_units(self, path):
        with open(path) as jsonfile:
            OrgUnitCreator(
                is_development=self.is_development_setup).run(jsonfile)


def opengever_content(setup):
    templates(setup)
    repository(setup)
    local_role_configuration(setup)


def templates(setup):
    data = setup.isDirectory(GEVER_CONTENT_FOLDER_NAME)
    if not data:
        return

    GeverContent(setup).install_templates()


class GeverContent(BaseSetupHandler):

    folder_name = GEVER_CONTENT_FOLDER_NAME

    def install_templates(self):
        transmogrifier = Transmogrifier(self.setup.getSite())
        transmogrifier(u'opengever.setup.content',
                       jsonsource=dict(directory=self.path))


def repository(setup):
    files = setup.listDirectory(setup._profile_path)
    if REPOSITORY_FILENAME not in files:
        return

    Repository(setup).install_repository()


class Repository(object):

    file_name = REPOSITORY_FILENAME

    def __init__(self, setup):
        self.setup = setup
        self.path = os.path.join(setup._profile_path,
                                 self.file_name).encode('utf-8')
        assert os.path.isfile(self.path)
        request = api.portal.get().REQUEST

        self.is_development_setup = request.get(
            'unit_creation_dev_mode', False)

    def install_repository(self):
        transmogrifier = Transmogrifier(self.setup.getSite())
        transmogrifier(u'opengever.setup.repository',
                       xlssource=dict(filename=self.path))


def local_role_configuration(setup):
    """Create local role setup.
    """
    data = setup.isDirectory(LOCAL_ROLE_CONFIGURATION_FOLDER_NAME)
    if not data:
        return

    LocalRoleConfiguration(setup).configure_local_roles()


class LocalRoleConfiguration(BaseSetupHandler):

    folder_name = LOCAL_ROLE_CONFIGURATION_FOLDER_NAME

    def configure_local_roles(self):
        transmogrifier = Transmogrifier(self.setup.getSite())
        transmogrifier(u'opengever.setup.local_roles',
                       jsonsource=dict(directory=self.path))
