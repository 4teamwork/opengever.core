from ftw.contentmenu.menu import FactoriesMenu
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.indexer.interfaces import IIndexableObject
from plone.testing.z2 import Browser
from zExceptions import Unauthorized
from zope.component import provideUtility
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import transaction
import unittest2 as unittest
from zope.schema import getFieldsInOrder


class DummyVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        # overwrite the contactsvocabulary utitlity with
        dummy_vocab = SimpleVocabulary(
            [SimpleTerm(value=u'contact:hugo.boss', title='Hugo Boss'),
             SimpleTerm(value=u'contact:james.bond', title='James Bond'), ])

        return dummy_vocab


class TestMainDossier(unittest.TestCase):
    """Base tests to test the default functions for all dossier-types

    let your testobject inherit from this class to extend it with default
    dossier-tests.
    The none-parameter-tests will start automatically, and the parameter-
    tests you have to call explicitly in a test_method:

    To set up a new test, you have to set in normal case this attributes:
    - dossier_types
    - layer
    - is_special_dossier
    """

    # Dossier-type you like to test
    # 1. typename
    # 2. map of additional schema behaviour to test
    # 3. additional attributes with value
    # example:dossier_types =
    #   {'opengever.zug.bdarp.casedossier1':
    #       {IARPCaseBehavior1:
    #           {'attr1':'val1', 'attr2':'sadfsadf'},
    #       {IARPCaseBehavior2:
    #           {'attr1':'val1', 'attr2':'sadfsadf'},
    #   {'opengever.zug.bdarp.casedossier2':
    #       {IARPCaseBehavior1:
    #           {'attr1':'val1', 'attr2':'sadfsadf'},
    #       {IARPCaseBehavior2:
    #           {'attr1':'val1', 'attr2':'sadfsadf'},
    # }}
    dossier_types = {'opengever.dossier.businesscasedossier': {}}
    # testlayer to use
    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING
    # Tabs to control
    tabs = ['Common', 'Filing', 'Life Cycle', 'Classification']
    # Defaultname of new dossiers
    dossier_id = 'dossier'
    # Repositoryname
    repo_id = 'repo'
    # new contents will be created in this folder
    location = 'http://nohost/plone/%s' % repo_id
    # Default labels to check
    labels = {'label_add': 'Add Subdossier',
              'label_edit': 'Edit Subdossier',
              'label_action': 'Subdossier',
             }
    # Deepth of subdossiers. How many times you can add a subdossier
    deepth = 1
    # Default dossier behavior
    default_behavior = IDossier
    # Default dossier behavior attributes
    defautl_attr = {'keywords': ['hallo', 'hugo']}
    # Is special dossier?
    is_special_dossier = False


    # Helpers
    # ***************************************************
    def get_browser(self):
        """Return logged in browser
        """
        # Create browser an login
        portal_url = self.layer['portal'].absolute_url()
        browser = Browser(self.layer['app'])
        browser.open('%s/login_form' % portal_url)
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

        # Check login
        self.assertNotEquals('__ac_name' in browser.contents, True)
        self.assertNotEquals('__ac_password' in browser.contents, True)

        return browser

    def get_add_view(self, dossier_type, path='', browser=None):
        """Return a browser whos content is in the add-view of a dossier
        """
        if not path:
            path = self.location

        if not browser:
            browser = self.get_browser()

        self.check_repo()

        browser.open('%s/++add++%s' % (path, dossier_type))
        return browser

    def get_edit_view(self, path, browser=None):
        """Return a browser whos content is in the edit-view of a dossier
        """
        if not browser:
            browser = self.get_browser()

        browser.open('%s/edit' % (path))
        return browser

    def create_dossier(self, dossier_type, subpath=''):
        """Create and return a dossier in a given location
        """
        self.check_repo()

        if subpath:
            subpath = "%s/%s" % (self.repo_id, subpath)
        else:
            subpath = self.repo_id
        obj = self.layer['portal'].restrictedTraverse(subpath)
        dossier = createContentInContainer(obj, dossier_type, title="Dossier")

        # XXX
        transaction.commit()
        return dossier

    def check_repo(self):
        """Create repository-folder
        """
        portal = self.layer['portal']
        if not portal.hasObject(self.repo_id):
            portal[portal.invokeFactory(
                'opengever.repository.repositoryfolder', self.repo_id)]

            transaction.commit()

    def map_with_vocab(self, behavior, fieldname, value):
        """Look in the schema for a vocab and return the mapped value
        """
        if type(value) == int:
            return str(value)

        if 'contact:' in value:
            # this is a hack for contacts because in tests
            # we dont have access to the ogds contacts an
            # we need to create a dummy-vocab
            voca = DummyVocabulary()(self.layer['portal'])
            return voca.by_value.get(value).title

        portal = self.layer['portal']
        fields = getFieldsInOrder(behavior)
        for name, field in fields:
            if name == fieldname and hasattr(field, 'value_type'):
                value_type = field.value_type
                if hasattr(value_type, 'vocabulary'):
                    vocab = value_type.vocabulary(portal)
                    value = vocab.by_value.get(value).title
        return value

    # tests
    # ***************************************************
    def test_content_types_installed(self):
        portal = self.layer['portal']
        types = portal.portal_types.objectIds()
        for dossier_type in self.dossier_types:
            self.assertTrue(dossier_type in types)

    def test_default_values(self):
        """Check the default values of the document
        """
        for dossier_type in self.dossier_types:
            browser = self.get_add_view(dossier_type)
            responsible = browser.getControl(
                name='form.widgets.IDossier.responsible.widgets.query').value
            self.assertNotEquals(None, responsible)

    def test_default_tabs(self):
        """Check default-tabs of the tabbedview.
        """

        for dossier_type in self.dossier_types:
            browser = self.get_add_view(dossier_type)

            for tab in self.tabs:

                # For exact search
                tab = "%s</legend>" % tab
                self.assertEquals(tab in browser.contents, True)

    def test_default_formular_labels(self):
        """Check default formular labels
        """
        for dossier_type in self.dossier_types:
            d1 = self.create_dossier(dossier_type)
            browser =self.get_browser()

            # Check action label
            menu = FactoriesMenu(d1)
            menu_items = menu.getMenuItems(d1, d1.REQUEST)

            # mails should never be addable in a dossier (over the menu)
            self.assertTrue(
                'ftw.mail.mail' not in [item.get('id') for item in menu_items])

            # a dossier in a dossier should called subdossier
            self.assertIn(
                self.labels.get('label_action'),
                [item.get('title') for item in menu_items])

            # Check add label
            browser = self.get_add_view(
                dossier_type, path=d1.absolute_url(), browser=browser)
            self.assertEquals(
                self.labels.get('label_add') in browser.contents, True)

            url = browser.url.split('/')[-1]
            self.assertTrue(url == '++add++%s' % dossier_type)

            # Check edit label
            d2 = self.create_dossier(dossier_type, subpath=d1.getId())
            browser = self.get_edit_view(d2.absolute_url(), browser=browser)
            self.assertEquals(
                self.labels.get('label_edit') in browser.contents, True)

    def test_nesting_deepth(self):
        """Check the deepth of subdossiers. Normally we just can add a
        subdossier to a dossier and the subdossier must be the same
        dossier-type like the parent-dossier. Its not possible to add
        a subdossier to a subdossier
        """

        for dossier_type in self.dossier_types:
            dossiers = []
            browser = self.get_browser()
            # First normal dossier
            dossiers.append(self.create_dossier(dossier_type))

            # Create subdossiers
            for i in range(self.deepth):

                path = []
                for dossier in dossiers:
                    path.append(dossier.getId())

                subdossier = self.create_dossier(
                    dossier_type, subpath="/".join(path))

                browser.open(subdossier.absolute_url())
                # its possible to add a subdossier
                if i < self.deepth-1:
                    # Check link is enabled
                    self.assertEquals(
                        self.labels.get('label_action') in browser.contents,
                        True)

                    # Check contenttype is allowed
                    self.assertIn(
                        dossier_type,
                        [fti.id for fti in subdossier.allowedContentTypes()])
                # its disallowed to add a subdossier
                else:
                    # Check link is disabled
                    self.assertNotEquals(
                        self.labels.get('label_action') in browser.contents,
                        True)
                    # Chekc contenttype is disallowed
                    self.assertTrue(
                        dossier_type not in [
                            fti.id for fti in
                            subdossier.allowedContentTypes()])

    def test_adding(self):
        if self.is_special_dossier:
            for dossier_type in self.dossier_types:
                portal = self.layer['portal']

                # Should not be addable in portal
                try:
                    portal.invokeFactory(
                        dossier_type, 'dossier1')
                    self.fail('Case dossier 1 should not be addable \
                                except within repository folders.')
                except (ValueError, Unauthorized):
                    pass

    def test_searchabletext(self):
        portal = self.layer['portal']
        provideUtility(
            DummyVocabulary(), name='opengever.ogds.base.ContactsVocabulary')

        for dossier_type, additional_behaviors in self.dossier_types.items():

            dossier = self.create_dossier(dossier_type)
            wrapper = queryMultiAdapter(
                (dossier, portal.portal_catalog), IIndexableObject)

            # set and search default dossier schema attributes
            schema = self.default_behavior(dossier)

            for attr, val in self.defautl_attr.items():
                schema.__setattr__(attr, val)

                if type(val) is list:
                    for v in val:
                        self.assertIn(v, wrapper.SearchableText)
                else:
                    self.assertIn(val, wrapper.SearchableText)

            # set and search additional dossier schema attributes
            if additional_behaviors:
                for behavior, attributes in additional_behaviors.items():
                    schema = behavior(dossier)
                    for attr, val in attributes.items():
                        # set value
                        schema.__setattr__(attr, val)
                        # search value
                        if type(val) is list:
                            for v in val:
                                v = self.map_with_vocab(behavior, attr, v)
                                self.assertIn(v, wrapper.SearchableText)
                        else:
                            val = self.map_with_vocab(behavior, attr, val)
                            self.assertIn(val, wrapper.SearchableText)

    def test_z_cleanup(self):
        """Cleanup the test-environment
        """
        # TODO: We need to reset the sequencenumber that other tests wont fail.
        # This implementation dont work.

        # Adjust the counter
        # new_counter_value = 0
        #         portal = self.layer['portal']
        #         ann = IAnnotations(portal)
        #         ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = PersistentDict()
        pass
