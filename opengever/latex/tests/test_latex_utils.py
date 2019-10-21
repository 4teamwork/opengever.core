from opengever.latex.utils import get_selected_items_from_catalog
from opengever.testing import IntegrationTestCase


class TestLatexUtils(IntegrationTestCase):

    def test_get_selected_items_from_catalog(self):
        self.login(self.regular_user)

        docs = [self.document, self.subdocument]

        # /plone/ordnungssystem
        paths = self.make_path_param(*docs)['paths:list']
        self.request['paths'] = paths

        items = list(get_selected_items_from_catalog(self.portal, self.request))

        self.assertItemsEqual(docs, [brain.getObject() for brain in items])

    def test_get_selected_items_from_catalog_with_pseudorelative_paths(self):
        self.login(self.regular_user)

        docs = [self.document, self.subdocument]

        # /ordnungssystem
        paths = self.make_pseudorelative_path_param(*docs)['paths:list']
        self.request['paths'] = paths

        items = list(get_selected_items_from_catalog(self.portal, self.request))

        self.assertItemsEqual(docs, [brain.getObject() for brain in items])
