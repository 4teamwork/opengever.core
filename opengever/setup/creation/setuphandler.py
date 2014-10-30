from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
import os


UNIT_CREATION_FOLDER_NAME = 'unit_creation'
ADMIN_UNIT_FILENAME = 'admin_units.json'
ORG_UNIT_FILENAME = 'org_units.json'

LOCAL_ROLE_CONFIGURATION_FOLDER_NAME = 'local_role_configuration'


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
            AdminUnitCreator().run(jsonfile)

    def create_org_units(self, path):
        with open(path) as jsonfile:
            OrgUnitCreator().run(jsonfile)

def opengever_content(setup):
    local_role_configuration(setup)


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
