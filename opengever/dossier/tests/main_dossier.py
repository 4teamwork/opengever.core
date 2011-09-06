from ftw.contentmenu.menu import FactoriesMenu
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME, login, logout
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
from AccessControl import getSecurityManager


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

    Params:

    - dossier-type: portal_type you like to test -->
        1. typename
        (for search)
        2. map of additional schema behaviour to test
        3. additional attributes with value
        example:dossier_types =
          {'opengever.zug.bdarp.casedossier1':
              {IARPCaseBehavior1:
                  {'attr1':'val1', 'attr2':'sadfsadf'},
              {IARPCaseBehavior2:
                  {'attr1':'val1', 'attr2':'sadfsadf'},
          {'opengever.zug.bdarp.casedossier2':
              {IARPCaseBehavior1:
                  {'attr1':'val1', 'attr2':'sadfsadf'},
              {IARPCaseBehavior2:
                  {'attr1':'val1', 'attr2':'sadfsadf'},
        }}

    - layer: testlayer to use
    - tabs: available tabs in the given order
    - repo_id: repositoryid
    - base_url: new content will be created in this folder
    - subdossier_labels: map with labels of subdossiers
    - deepth: how deepth you can add subdossiers
    - default_behavior: schema-behavior of default dossier
    - default_attr: attributes to test in the default behavior
    - is_special_dossier: if true, that we can add this dossie just in a repos
    """
    dossier_types = {'opengever.dossier.businesscasedossier': {}}
    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING
    tabs = ['Overview',
            'Subdossiers',
            'Documents',
            'Tasks',
            'Participants',
            'Trash',
            'Journal',
            'Sharing', ]
    repo_id = 'repo'
    base_url = 'http://nohost/plone/%s' % repo_id
    subdossier_labels = {'label_add': 'Add Subdossier',
                          'label_edit': 'Edit Subdossier',
                          'label_action': 'Subdossier',
             }
    deepth = 1
    default_behavior = IDossier
    defautl_attr = {'keywords': ['hallo', 'hugo']}
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
            path = self.base_url

        if not browser:
            browser = self.get_browser()

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

        if subpath:
            subpath = "%s/%s" % (self.repo_id, subpath)
        else:
            subpath = self.repo_id
        obj = self.layer['portal'].restrictedTraverse(subpath)
        dossier = createContentInContainer(obj, dossier_type, title="Dossier")

        # XXX
        transaction.commit()
        return dossier

    def get_logged_in_user(self):
        return getSecurityManager().getUser().getId()

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
            if name == fieldname:

                # We have different types of fields, so we have to check,
                # that we become the vocabulary
                value_type = field
                if hasattr(field, 'value_type'):
                    value_type = field.value_type

                if hasattr(value_type, 'vocabulary'):
                    vocab = value_type.vocabulary(portal)
                    value = vocab.by_value.get(value).title
        return value

    # tests
    # ***************************************************
    #
    def setUp(self):
        """Set up the testenvironment
        """
        portal = self.layer['portal']
        if not portal.hasObject(self.repo_id):
            portal[portal.invokeFactory(
                'opengever.repository.repositoryfolder', self.repo_id)]

            transaction.commit()

    def test_content_types_installed(self):
        """Check whether the content-type is installed
        """
        portal = self.layer['portal']
        types = portal.portal_types.objectIds()
        for dossier_type in self.dossier_types:
            self.assertTrue(dossier_type in types)

    def test_default_values(self):
        """Check the default values of the dossier
        Default responsible of a new dossier must be the owner. The
        default responsible of a subdossier must be the owner of the
        parent-dossier
        """

        for dossier_type in self.dossier_types:
            # browser = self.get_add_view(dossier_type)
            portal = self.layer['portal']
            request = self.layer['request']
            request.set('form.widgets.IDossier.responsible', [])

            d1_view = portal.repo.unrestrictedTraverse(
                '++add++%s' % dossier_type)
            # We have to call the view to run the update-method
            d1_view()

            # In the request we must have the logged in user
            self.assertEquals([self.get_logged_in_user()], d1_view.request.get(
                'form.widgets.IDossier.responsible', None))

            # In tests, the default value from the request won't work correctly
            # So we create a new dossier and add the resposible manually
            d1 = self.create_dossier(dossier_type)

            # set the responsible
            IDossier(d1).responsible = self.get_logged_in_user()

            # We have to reset the request for the new dossier
            request.set('form.widgets.IDossier.responsible', [])

            logout()
            login(portal, SITE_OWNER_NAME)

            # The same with another user
            d2_view = portal.repo.unrestrictedTraverse(
                '++add++%s' % dossier_type)
            d2_view()
            self.assertEquals([self.get_logged_in_user()], d2_view.request.get(
                'form.widgets.IDossier.responsible', None))
            d2 = self.create_dossier(dossier_type)
            IDossier(d2).responsible = self.get_logged_in_user()
            request.set('form.widgets.IDossier.responsible', [])

            # We change the user again an create a subdossier
            logout()
            login(portal, TEST_USER_NAME)

            d2_1_view = d2.unrestrictedTraverse('++add++%s' % dossier_type)
            d2_1_view()

            # This is a subdossier, so in responsible we must have the responsible
            # of the parent
            self.assertEquals(
                [IDossier(d2).responsible],
                d2_1_view.request.get(
                    'form.widgets.IDossier.responsible', None))

    def test_default_tabs(self):
        """Check default-tabs and order of the tabbedview.
        """
        portal = self.layer['portal']
        types_tool = portal.portal_types

        for dossier_type in self.dossier_types:

            # Copy of tabs, because we pop the tab if we found one.
            # If we take the original, and we have more than one
            # dossier_type, then the second and all other dossier_types
            # are true.
            tabs = self.tabs
            obj = self.create_dossier(dossier_type)
            actions = types_tool.listActions(object=obj)
            for action in actions:
                if action.category == 'tabbedview-tabs':
                    # if its a default-tab in the correct order
                    # we pop it from the tabs-list
                    if action.title in tabs and tabs.index(action.title) == 0:
                        tabs.pop(0)

            # the tabs-var should be empty if we found every tab
            self.assertEquals(tabs, [])

    def test_default_subdossier_labels(self):
        """Check default form labels of subdossier
        We have a special handling of labels in subdossiers.
        We have different specialdossies, but we always have the same
        text in the add, edit and action-view.
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
                self.subdossier_labels.get('label_action'),
                [item.get('title') for item in menu_items])

            # Check add label
            browser = self.get_add_view(
                dossier_type, path=d1.absolute_url(), browser=browser)
            self.assertEquals(
                self.subdossier_labels.get(
                    'label_add') in browser.contents, True)

            url = browser.url.split('/')[-1]
            self.assertTrue(url == '++add++%s' % dossier_type)

            # Check edit label
            d2 = self.create_dossier(dossier_type, subpath=d1.getId())
            browser = self.get_edit_view(d2.absolute_url(), browser=browser)
            self.assertEquals(
                self.subdossier_labels.get(
                    'label_edit') in browser.contents, True)

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

                dossiers.append(subdossier)

                browser.open(subdossier.absolute_url())
                # its possible to add a subdossier
                if i < self.deepth-1:
                    # Check link is enabled
                    self.assertEquals(
                        self.subdossier_labels.get(
                            'label_action') in browser.contents, True)

                    # Check contenttype is allowed
                    self.assertIn(
                        dossier_type,
                        [fti.id for fti in subdossier.allowedContentTypes()])
                # its disallowed to add a subdossier
                else:
                    # Check link is disabled
                    self.assertNotEquals(
                        self.subdossier_labels.get(
                            'label_action') in browser.contents, True)
                    # Chekc contenttype is disallowed
                    self.assertTrue(
                        dossier_type not in [
                            fti.id for fti in
                            subdossier.allowedContentTypes()])

    def test_not_addable(self):
        """check whether the dossier is not addable
        """
        if self.is_special_dossier:
            for dossier_type in self.dossier_types:
                portal = self.layer['portal']

                # Should not be addable in portal
                try:
                    portal.invokeFactory(
                        dossier_type, 'dossier1')

                    # if we can add the dossier, we have to raise an error
                    self.fail('Case dossier 1 should not be addable \
                                except within repository folders.')
                except (ValueError, Unauthorized):
                    # if we can't add the dossier, everything is ok
                    pass

    def test_searchabletext(self):
        """Check the searchable text of an object
        """
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
                                val = self.map_with_vocab(behavior, attr, v)

                        else:
                            val = self.map_with_vocab(behavior, attr, val)

                        self.assertIn(
                            val.encode('utf-8'), wrapper.SearchableText)

    def tearDown(self):
        """Cleanup the test-environment after each test
        """
        # TODO: We need to reset the sequencenumber that other tests wont fail.
        # This implementation dont work.

        # Adjust the counter
        # new_counter_value = 0
        #         portal = self.layer['portal']
        #         ann = IAnnotations(portal)
        #         ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = PersistentDict()
        pass
