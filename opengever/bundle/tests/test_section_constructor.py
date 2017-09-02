from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.bundle.sections.constructor import ConstructorSection
from opengever.bundle.sections.constructor import InvalidType
from opengever.bundle.tests import MockBundle
from opengever.bundle.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestConstructor(FunctionalTestCase):

    def setUp(self):
        super(TestConstructor, self).setUp()

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        # Required to create mails, but not dossiers - no idea why
        self.grant('Manager')

    def setup_section(self, previous=None):
        previous = previous or []
        transmogrifier = MockTransmogrifier()
        IAnnotations(transmogrifier)[BUNDLE_KEY] = MockBundle()
        options = {}

        return ConstructorSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(ConstructorSection))
        verifyClass(ISection, ConstructorSection)

        self.assertTrue(ISectionBlueprint.providedBy(ConstructorSection))
        verifyObject(ISectionBlueprint, ConstructorSection)

    def test_raises_for_invalid_types(self):
        section = self.setup_section(previous=[{
            "guid": "12345xy",
            "_type": "foo.bar.qux",
        }])
        with self.assertRaises(InvalidType):
            list(section)

    def test_updates_item_with_object_information(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"opengever.repository.repositoryroot",
            u"title_de": u"Reporoot",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        obj = portal.restrictedTraverse(item['_path'])

        self.assertEqual('reporoot', item['_path'])
        self.assertEqual(portal.get('reporoot'), obj)

    def test_creates_itranslated_title_content(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"opengever.repository.repositoryroot",
            u"title_de": u"Reporoot",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        content = portal.get('reporoot')
        self.assertIsNotNone(content)
        self.assertEqual(u'Reporoot', content.title_de)
        self.assertIsNone(content.title_fr)

    def test_creates_simple_title_content(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"opengever.dossier.businesscasedossier",
            u"title": u"Dossier",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(u'Dossier', content.title)
        self.assertFalse(hasattr(content, 'title_de'))
        self.assertFalse(hasattr(content, 'title_Fr'))

    def test_sets_bundle_guid_on_obj(self):
        guid = "12345xy"
        item = {
            u"guid": guid,
            u"_type": u"opengever.dossier.businesscasedossier",
            u"title": u"My Dossier",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(guid, IAnnotations(content)[BUNDLE_GUID_KEY])

    def test_catalog(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"opengever.repository.repositoryroot",
            u"title_de": u"Reporoot",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        obj_path = '/'.join(portal.getPhysicalPath() + (item['_path'],))

        query = {'path': {'query': obj_path,
                          'depth': 0}}

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(query)
        self.assertEqual(len(brains), 1)

        obj_brain = brains[0]
        self.assertEqual(obj_brain.portal_type,
                         'opengever.repository.repositoryroot')
        self.assertEqual(obj_brain.Title, u'Reporoot')

    def test_can_create_eml_emails(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"ftw.mail.mail",
            u"title": u"My Mail",
            u"_path": u"/foo/bar"
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(u'My Mail', content.title)
        self.assertFalse(hasattr(content, 'title_de'))
        self.assertFalse(hasattr(content, 'title_Fr'))
