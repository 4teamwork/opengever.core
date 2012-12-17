from Missing import Value as MissingValue
from Products.ZCatalog.interfaces import ICatalogBrain
from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.contentlisting.interfaces import IContentListingObject


class ZCMLLayer(ComponentRegistryLayer):
    """Test layer loading the complete package ZCML.
    """

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        import opengever.base.tests
        self.load_zcml_file('tests.zcml', opengever.base.tests)

ZCML_LAYER = ZCMLLayer()


class TestOpengeverContentListing(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestOpengeverContentListing, self).setUp()
        self.brain = self.providing_stub([ICatalogBrain, ])
        self.request = self.stub_request()
        self.expect(self.brain.REQUEST).result(self.request)
        self.expect(self.brain.getPath(), 'Fake Path')

    def test_containing_dossier(self):
        """the containg dossier should be cropped to 200 items."""
        self.expect(
            self.brain.containing_dossier).result(
            10 * 'Lorem ipsum dolor sit amet')

        self.replay()
        self.assertEquals(
            len(IContentListingObject(self.brain).containing_dossier()),
            203)

    def test_containing_dosssier_without_value(self):
        self.expect(self.brain.containing_dossier).result(None)
        self.replay()
        self.assertEquals(
            IContentListingObject(self.brain).containing_dossier(), '')

    def test_containing_dosssier_with_missing_value(self):
        self.expect(self.brain.containing_dossier).result(MissingValue)
        self.replay()
        self.assertEquals(
            IContentListingObject(self.brain).containing_dossier(), '')

    def test_title(self):
        """the title should be cropped to circa 200 characters."""
        self.expect(self.brain.Title).result(
            10 * 'Lorem ipsum dolor sit amet')

        self.replay()
        self.assertEquals(
            len(IContentListingObject(self.brain).CroppedTitle()), 203)

    def test_title_without_value(self):
        self.expect(self.brain.Title).result(None)

        self.replay()
        self.assertEquals(IContentListingObject(self.brain).CroppedTitle(), '')

    def test_title_with_missing_value(self):
        self.expect(self.brain.Title).result(MissingValue)

        self.replay()
        self.assertEquals(IContentListingObject(self.brain).CroppedTitle(), '')

    def test_description(self):
        """the description should be cropped to circa 400 characters."""
        self.expect(self.brain.Description).result(
            20 * 'Lorem ipsum dolor sit amet')

        self.replay()
        self.assertEquals(
            len(IContentListingObject(self.brain).CroppedDescription()), 399)

    def test_description_without_value(self):
        self.expect(self.brain.Description).result(None)

        self.replay()
        self.assertEquals(
            IContentListingObject(self.brain).CroppedDescription(), '')

    def test_description_with_missing_value(self):
        self.expect(self.brain.Description).result(MissingValue)

        self.replay()
        self.assertEquals(
            IContentListingObject(self.brain).CroppedDescription(), '')
