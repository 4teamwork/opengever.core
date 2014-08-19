from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
import os


FOLDER_NAME = 'unit_creation'
ADMIN_UNIT_FILENAME = 'admin_units.json'
ORG_UNIT_FILENAME = 'org_units.json'


def unit_creation(setup):
    """Create initial Org-Unitds Admin-Units.
    """
    data = setup.isDirectory(FOLDER_NAME)
    if not data:
        return

    UnitCreation(setup).create_units()


class UnitCreation(object):

    def __init__(self, setup):
        self.setup = setup
        self.path = os.path.join(setup._profile_path,
                                 FOLDER_NAME).encode('utf-8')
        assert os.path.isdir(self.path)

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
