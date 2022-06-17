from Acquisition import aq_base
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.bundle.sections.constructor import ConstructorSection
from opengever.bundle.sections.constructor import InvalidType
from opengever.bundle.tests import MockBundle
from opengever.bundle.tests import MockTransmogrifier
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestConstructor(IntegrationTestCase):

    def setUp(self):
        super(TestConstructor, self).setUp()

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

        # All bundle migration are always run with the system user
        self.login(self.manager)

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
            "parent_guid": "123_parent",
            "_type": "foo.bar.qux",
        }])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.leaf_repofolder.getPhysicalPath()[2:])
        }

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
        self.assertIsNone(content.title_en)

    def test_creates_itranslated_title_content_with_multiple_languages(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"opengever.repository.repositoryroot",
            u"title_de": u"Ordn\xfcngsposition",
            u"title_fr": u"Position",
            u"title_en": u"Reporoot",
        }
        section = self.setup_section(previous=[item])
        list(section)

        portal = api.portal.get()
        content = portal.get('ordnuengsposition')
        self.assertIsNotNone(content)
        self.assertEqual(u'Ordn\xfcngsposition', content.title_de)
        self.assertEqual(u'Reporoot', content.title_en)
        self.assertEqual(u'Position', content.title_fr)

    def test_creates_simple_title_content(self):
        item = {
            u"guid": "12345xy",
            u"parent_guid": "123_parent",
            u"_type": u"opengever.dossier.businesscasedossier",
            u"title": u"Dossier",
        }

        section = self.setup_section(previous=[item])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.leaf_repofolder.getPhysicalPath()[2:])
        }
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(u'Dossier', content.title)
        self.assertFalse(hasattr(aq_base(content), 'title_de'))
        self.assertFalse(hasattr(aq_base(content), 'title_fr'))
        self.assertFalse(hasattr(aq_base(content), 'title_en'))

    def test_title_is_unicode(self):
        item = {
            u"guid": "12345xy",
            u"parent_guid": "123_parent",
            u"_type": u"opengever.document.document",
            u"title": u'Bewerbung Hanspeter M\xfcller'.encode('utf-8'),
        }

        section = self.setup_section(previous=[item])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.dossier.getPhysicalPath()[2:])
        }
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertTrue(isinstance(content.title, unicode))
        self.assertEquals(u'Bewerbung Hanspeter M\xfcller', content.title)

    def test_populates_path_by_refnum_cache(self):
        items = [
            {'guid': 'a1',
             '_type': 'opengever.dossier.businesscasedossier',
             '_formatted_parent_refnum': 'Client1 1.1 / 1',
             'parent_reference': [[1, 1], [1]]},

            {'guid': 'b1',
             '_type': 'opengever.dossier.businesscasedossier',
             '_formatted_parent_refnum': 'Client1 1.1',
             'parent_reference': [[1, 1]]}
        ]
        section = self.setup_section(previous=items)
        list(section)

        self.assertEqual(
            {'Client1 1.1': 'ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
             'Client1 1.1 / 1': 'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
            section.bundle.path_by_refnum_cache)

    def test_sets_bundle_guid_on_obj(self):
        guid = "12345xy"
        item = {
            u"guid": guid,
            u"parent_guid": "123_parent",
            u"_type": u"opengever.dossier.businesscasedossier",
            u"title": u"My Dossier",
        }
        section = self.setup_section(previous=[item])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.leaf_repofolder.getPhysicalPath()[2:])
        }
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
            u"parent_guid": "123_parent",
            u"title": u"My Mail",
            u"_path": u"/foo/bar"
        }
        section = self.setup_section(previous=[item])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.dossier.getPhysicalPath()[2:])
        }
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(u'My Mail', content.title)
        self.assertFalse(hasattr(aq_base(content), 'title_de'))
        self.assertFalse(hasattr(aq_base(content), 'title_fr'))
        self.assertFalse(hasattr(aq_base(content), 'title_en'))

    def test_use_formatted_parent_refnum_for_container_path(self):
        item = {
            u"guid": "12345xy",
            u"_type": u"ftw.mail.mail",
            u"_formatted_parent_refnum": "Client 1.1 / 1",
            u"title": u"My Mail",
            u"_path": u"/foo/bar"
        }

        section = self.setup_section(previous=[item])
        path = '/'.join(self.dossier.getPhysicalPath()[2:])
        section.bundle.path_by_refnum_cache["Client 1.1 / 1"] = path
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        self.assertEqual(u'My Mail', content.title)
        self.assertEqual('ftw.mail.mail', content.portal_type)

    def test_journal_entry_made_as_creator(self):
        item = {
            u"guid": "12345xy",
            u"parent_guid": "123_parent",
            u"_type": u"opengever.dossier.businesscasedossier",
            u"_creator": self.regular_user.id,
            u"title": u"Dossier",
        }

        section = self.setup_section(previous=[item])
        section.bundle.item_by_guid['123_parent'] = {
            '_path': '/'.join(self.leaf_repofolder.getPhysicalPath()[2:])
        }
        list(section)

        portal = api.portal.get()
        content = portal.restrictedTraverse(item['_path'])

        entry = get_journal_entry(content)

        self.assertEqual(u'Dossier', content.title)
        self.assertEqual('Dossier added', entry['action']['type'])
        self.assertEqual(self.regular_user.id, entry['actor'])
