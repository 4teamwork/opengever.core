from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import datetime
from ftw.testing import freeze
from opengever.bundle.console import add_guid_index
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestInitialContentCreation(FunctionalTestCase):

    def test_oggbundle_transmogrifier(self):
        add_guid_index()

        self.grant("Manager")
        transmogrifier = Transmogrifier(api.portal.get())
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = resource_filename(
            'opengever.bundle.tests',
            'assets/initial_content.oggbundle')

        mtool = api.portal.get_tool('portal_membership')
        mtool.memberareaCreationFlag = 0

        with freeze(FROZEN_NOW):
            transmogrifier(u'opengever.bundle.oggbundle')

        inboxcontainer = self.assert_inboxcontainer_created()
        self.assert_inboxes_created(inboxcontainer)
        self.assert_private_root_created(mtool)
        self.assert_templatefolder_created()

    def assert_inboxcontainer_created(self):
        inboxcontainer = self.portal.get('eingangskorb')
        self.assertEqual(u'Eingangskorb', inboxcontainer.title_de)
        self.assertEqual(u'Bo\xeete de r\xe9ception', inboxcontainer.title_fr)
        self.assertEqual(
            'inbox-state-default',
            api.content.get_state(inboxcontainer))

        return inboxcontainer

    def assert_inboxes_created(self, inboxcontainer):
        inbox_fd = inboxcontainer.get('finanzdepartement')
        self.assertEqual(
            u'finanzdepartement',
            IResponsibleOrgUnit(inbox_fd).responsible_org_unit)
        self.assertEqual(
            u'Eingangskorb FD - Finanzdepartement',
            inbox_fd.title_de)
        self.assertEqual(
            u'Bo\xeete de r\xe9ception FD - Finanzdepartement',
            inbox_fd.title_fr)
        self.assertEqual(
            'inbox-state-default',
            api.content.get_state(inbox_fd))

        inbox_bd = inboxcontainer.get('baudepartement')
        self.assertEqual(
            u'baudepartement',
            IResponsibleOrgUnit(inbox_bd).responsible_org_unit)
        self.assertEqual(
            u'Eingangskorb BD - Baudepartement',
            inbox_bd.title_de)
        self.assertEqual(
            u'Bo\xeete de r\xe9ception BD - Baudepartement',
            inbox_bd.title_fr)
        self.assertEqual(
            'inbox-state-default',
            api.content.get_state(inbox_bd))

    def assert_private_root_created(self, mtool):
        private_root = self.portal.get('private')
        self.assertEqual('Meine Ablage', private_root.title_de)
        self.assertEqual('Dossier personnel', private_root.title_fr)
        self.assertEqual(
            'repositoryroot-state-active',  # [sic] WF contains typo
            api.content.get_state(private_root))

        # Feature should be enabled after private root import
        self.assertEqual(1, mtool.getMemberareaCreationFlag())

        return private_root

    def assert_templatefolder_created(self):
        templatefolder = self.portal.get('vorlagen')
        self.assertEqual(u'Vorlagen', templatefolder.title_de)
        self.assertEqual(u'Mod\xe8les', templatefolder.title_fr)
        self.assertEqual(
            'templatefolder-state-active',
            api.content.get_state(templatefolder))

        return templatefolder
