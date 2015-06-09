from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.creator import ICreatorAware
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestCreatorBehavior(FunctionalTestCase):
    """
    The Creator behavior sets the creator an content creation.
    It also adds a creators field with listCreators() and setCreators()
    methods. The field is hidden by default.
    """

    def setUp(self):
        super(TestCreatorBehavior, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_creator_field_is_hidden_by_default(self, browser):
        browser.login().open(self.dossier)
        factoriesmenu.add('Document')
        self.assertNotIn('Creators', browser.forms.get('form').field_labels)

    def test_creator_is_set_when_creating_objects(self):
        document = create(Builder('document').within(self.dossier))
        self.assertEquals((TEST_USER_ID,), document.listCreators())
        self.assertEquals(TEST_USER_ID, document.Creator())

    def test_marker_interface_is_provided_by_objects_with_behavior(self):
        document = create(Builder('document').within(self.dossier))
        self.assertTrue(ICreatorAware.providedBy(document))

    def test_creator_setter(self):
        document = create(Builder('document').within(self.dossier))

        document.setCreators(('foo',))
        self.assertEquals(('foo',), document.listCreators())

        document.addCreator('bar')
        self.assertEquals(('foo', 'bar'), document.listCreators())
