from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.base.interfaces import IWhiteLabelingSettings
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from plone import api
import json
import os


UNIT_CREATION_FOLDER_NAME = 'unit_creation'
ADMIN_UNIT_FILENAME = 'admin_units.json'
ORG_UNIT_FILENAME = 'org_units.json'

LOCAL_ROLE_CONFIGURATION_FOLDER_NAME = 'local_role_configuration'

GEVER_CONTENT_FOLDER_NAME = 'opengever_content'

DEVELOP_USERS_GROUP = 'og_demo-ftw_users'

REPOSITORIES_FOLDER_NAME = 'opengever_repositories'


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
    repositories(setup)
    templates(setup)
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


def repositories(setup):
    data = setup.isDirectory(REPOSITORIES_FOLDER_NAME)
    if not data:
        return

    Repositories(setup).install()


class Repositories(BaseSetupHandler):

    folder_name = REPOSITORIES_FOLDER_NAME

    def install(self):
        transmogrifier = Transmogrifier(self.setup.getSite())
        transmogrifier(u'opengever.setup.repository',
                       xlssource=dict(directory=self.path))


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


def set_geverui_white_labeling_settings(context):
    logo_image = context.readDataFile('white_labeling/customer_logo.png')
    if logo_image:
        api.portal.set_registry_record('logo_src', logo_image, interface=IWhiteLabelingSettings)

    settings_file = context.readDataFile('white_labeling/settings.json')
    if settings_file:
        settings = json.loads(settings_file)
        seperately_treated_fields = ['color_scheme_light', 'dossier_type_colors', 'logo_src']
        white_labeling_fields = [field for field in IWhiteLabelingSettings.names()
                                 if field not in seperately_treated_fields]
        for field in white_labeling_fields:
            if field in settings:
                api.portal.set_registry_record(
                    field, settings[field], interface=IWhiteLabelingSettings)
        if 'color_scheme_light' in settings:
            api.portal.set_registry_record(
                'color_scheme_light',
                json.dumps(settings['color_scheme_light'], ensure_ascii=False),
                interface=IWhiteLabelingSettings)

        if 'dossier_type_colors' in settings:
            api.portal.set_registry_record(
                'dossier_type_colors',
                json.dumps(settings['dossier_type_colors'], ensure_ascii=False),
                interface=IWhiteLabelingSettings)
