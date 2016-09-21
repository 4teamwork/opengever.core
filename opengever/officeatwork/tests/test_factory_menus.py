from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from opengever.core.testing import OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER
from opengever.testing import FunctionalTestCase


class TestOfficeatworkFactoryMenus(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER

    def test_factory_menu_enabled_for_businesscasedossier(self):
        dossier = create(Builder('dossier'))
        menu = FactoriesMenu(dossier)
        menu_items = menu.getMenuItems(dossier, dossier.REQUEST)

        self.assertEquals(
            ['Document',
             'document_with_template',
             'document_from_officeatwork',
             'Task',
             'Add task from template',
             'Subdossier',
             'Participant'],
            [item.get('title') for item in menu_items])
