# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from ftw.contentmenu.menu import FactoriesMenu
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import create_plone_user
from opengever.testing import set_current_client_id
from plone.app.testing import SITE_OWNER_NAME, login, logout
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.indexer.interfaces import IIndexableObject
from zExceptions import Unauthorized
from zope.component import getAdapter, getUtility
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IChoice, IList, ITuple
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.vocabulary import getVocabularyRegistry
import transaction


class DummyVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        # overwrite the contactsvocabulary utitlity with
        dummy_vocab = SimpleVocabulary(
            [SimpleTerm(value=u'contact:hugo.boss', title='Hugo Boss'),
             SimpleTerm(value=u'contact:james.bond', title='James Bond'), ])

        return dummy_vocab


class TestMainDossier(FunctionalTestCase):
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
        2. additional attributes to search with value to set
        example:dossier_types =
          {'opengever.zug.bdarp.casedossier1':
              {'search_attr1':'val1', 'search_attr2':'sadfsadf'},
          {'opengever.zug.bdarp.casedossier2':
              {'search_attr1':'val1', 'search_attr2':'sadfsadf'},
        }}

    - layer: testlayer to use
    - tabs: available tabs in the given order
    - repo_id: repositoryid
    - base_url: new content will be created in this folder
    - labels: map with labels of subdossiers
    - deepth: how deepth you can add subdossiers
    - default_searchable_attr: attributes to test the searchable text: special:
        reference_number to test, set it to 'test_reference_number'
        sequence_number to test, set it to 'test_sequence_number'
        filing_no to test, set it to 'test_filing_no'
        otherwise remove the attrs
    - is_special_dossier: if true, that we can add this dossie just in a repos
    - default_contentmenu_order: The orderposition of items in the content-menu.
    - default_contentmenu_order_subdossier: The orderposition of items in the
        contentmenu for subdossiers
    """
    use_browser = True

    dossier_types = {'opengever.dossier.businesscasedossier': {}}

    workflow = "opengever_dossier_workflow"

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

    labels = {'add_subdossier': 'Add Subdossier',
              'edit_subdossier': 'Edit Subdossier',
              'action_name': 'Subdossier',
             }

    deepth = 1

    default_searchable_attr = {'reference_number': 'test_reference_number',
                                'sequence_number': 'test_sequence_number',
                               'filing_no': 'test_filing_no',
                               'comments': u'wir wollen James "Bond" überall',
                               'keywords': ['hallo', 'hugo']}

    is_special_dossier = False

    default_contentmenu_order = ['Document',
                                 'Document with docucomposer',
                                 'document_with_template',
                                 'Task',
                                 'Add task from template',
                                 'Subdossier',
                                 'Add Participant',
                                ]

    default_contentmenu_order_subdossier = ['Document',
                                            'Document with docucomposer',
                                            'document_with_template',
                                            'Task',
                                            'Add task from template',
                                            'Add Participant',
                                           ]

    def get_add_view(self, dossier_type, path=''):
        """Return a browser whos content is in the add-view of a dossier
        """
        if not path:
            path = self.base_url

        self.browser.open('%s/++add++%s' % (path, dossier_type))

    def get_edit_view(self, path):
        """Return a browser whos content is in the edit-view of a dossier
        """
        self.browser.open('%s/edit' % (path))

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

        portal = self.layer['portal']
        fields = getFieldsInOrder(behavior)
        for name, field in fields:
            if name == fieldname:

                # We have different types of fields, so we have to check,
                # that we become the vocabulary
                value_type = field

                if IList.providedBy(field) or ITuple.providedBy(field):
                    value_type = field.value_type

                if IChoice.providedBy(value_type):
                    if value_type.vocabulary:
                        vocab = value_type.vocabulary(portal)

                    else:
                        vocab = getVocabularyRegistry().get(
                            portal, value_type.vocabularyName)

                    value = vocab.getTerm(value).title

        return value

    # tests
    # ***************************************************
    #
    def setUp(self):
        """Set up the testenvironment
        """
        super(TestMainDossier, self).setUp()
        self.grant('Contributor')

        create_client()
        set_current_client_id(self.portal)

        create_plone_user(self.portal, SITE_OWNER_NAME)
        create_ogds_user(SITE_OWNER_NAME)

        self.request = self.layer['request']

        if not self.portal.hasObject(self.repo_id):
            self.repo = self.portal[self.portal.invokeFactory(
                'opengever.repository.repositoryfolder', self.repo_id)]

        self._utilities = []

        transaction.commit()

    def test_content_types_installed(self):
        """Check whether the content-type is installed
        """
        types = self.portal.portal_types.objectIds()
        for dossier_type in self.dossier_types:
            self.assertTrue(dossier_type in types)

    def test_sendable_docs_containter(self):
        """Check if all dossiers provide the ISendableDocsContainer
        Interface."""

        for dossier_type in self.dossier_types:
            d1 = self.create_dossier(dossier_type)
            d2 = self.create_dossier(dossier_type, subpath=d1.getId())

            self.assertTrue(ISendableDocsContainer.providedBy(d1))
            self.assertTrue(ISendableDocsContainer.providedBy(d2))

    def test_contentmenu_order_positions(self):
        """Check the order of the add-menu for dossiers and subdossiers
        """
        for dossier_type in self.dossier_types:
            d1 = self.create_dossier(dossier_type)
            d2 = self.create_dossier(dossier_type, subpath=d1.getId())

            # Check action label
            menu = FactoriesMenu(d1)
            menu2 = FactoriesMenu(d2)

            menu_items = menu.getMenuItems(d1, d1.REQUEST)
            menu_items2 = menu2.getMenuItems(d2, d2.REQUEST)

            # For dossiers
            for i, ordered_item in enumerate(self.default_contentmenu_order):

                menu_item_titles = [item['title'] for item in menu_items]

                # The item must be in the contentmenu
                self.assertTrue(ordered_item in menu_item_titles)

                # And must be in the correct position
                self.assertTrue(ordered_item == menu_item_titles[i])

            # For subdossiers
            for i, ordered_item in enumerate(
                self.default_contentmenu_order_subdossier):

                menu_item_titles2 = [item['title'] for item in menu_items2]

                # The item must be in the contentmenu
                self.assertTrue(ordered_item in menu_item_titles2)

                # And must be in the correct position
                self.assertTrue(ordered_item == menu_item_titles2[i])

    def test_workflows_mapped(self):
        """Check wheter the workflow is mapped correctly
        """
        wftool = getToolByName(self.portal, 'portal_workflow')

        for dossier_type in self.dossier_types:
            self.assertTrue(
                self.workflow in \
                    wftool.getWorkflowsFor(
                        dossier_type)[0].getId())

    def test_default_values(self):
        """Check the default values of the dossier
        Default responsible of a new dossier must be the owner. The
        default responsible of a subdossier must be the owner of the
        parent-dossier
        """

        for dossier_type in self.dossier_types:
            # browser = self.get_add_view(dossier_type)

            self.request.set('form.widgets.IDossier.responsible', [])

            d1_view = self.portal.repo.unrestrictedTraverse(
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
            self.request.set('form.widgets.IDossier.responsible', [])

            logout()
            login(self.portal, SITE_OWNER_NAME)

            # The same with another user
            d2_view = self.portal.repo.unrestrictedTraverse(
                '++add++%s' % dossier_type)
            d2_view()
            self.assertEquals([self.get_logged_in_user()], d2_view.request.get(
                'form.widgets.IDossier.responsible', None))
            d2 = self.create_dossier(dossier_type)
            IDossier(d2).responsible = self.get_logged_in_user()
            self.request.set('form.widgets.IDossier.responsible', [])

            # We change the user again an create a subdossier
            logout()
            login(self.portal, TEST_USER_NAME)

            d2_1_view = d2.unrestrictedTraverse('++add++%s' % dossier_type)
            d2_1_view()

            # This is a subdossier, so in responsible
            # we must have the responsible of the parent
            self.assertEquals(
                [IDossier(d2).responsible],
                d2_1_view.request.get(
                    'form.widgets.IDossier.responsible', None))

    def test_default_tabs(self):
        """Check default-tabs and tabs-order
        """
        types_tool = getToolByName(self.portal, 'portal_types')

        for dossier_type in self.dossier_types:

            # Copy of tabs, because we pop the tab if we found one.
            # If we take the original, and we have more than one
            # dossier_type, then the second and all other dossier_types
            # are true.
            tabs = self.tabs
            obj = self.create_dossier(dossier_type)
            actions = types_tool.listActions(object=obj)
            for action in actions:
                if not action.category == 'tabbedview-tabs':
                    continue

                # if its a default-tab in the correct order
                # we pop it from the tabs-list
                if action.title in tabs and tabs.index(action.title) == 0:
                    tabs.pop(0)

            # the tabs-var should be empty if we found every tab
            self.assertEquals(tabs, [])

    def test_special_overview(self):
        """check if the additional attributes are display in the overview"""
        for dossier_type in self.dossier_types:
            if self.is_special_dossier:
                d1 = self.create_dossier(dossier_type)
                url = '%s/tabbedview_view-overview' %(d1.absolute_url())
                self.browser.open(url)
                self.assertTrue('additional_attributes' in self.browser.contents)

    def test_default_labels(self):
        """Check default form labels of subdossier
        We have a special handling of labels in subdossiers.
        We have different specialdossies, but we always have the same
        text in the add, edit and action-view.
        """
        for dossier_type in self.dossier_types:
            d1 = self.create_dossier(dossier_type)

            # Check action label
            menu = FactoriesMenu(d1)
            menu_items = menu.getMenuItems(d1, d1.REQUEST)

            # mails should never be addable in a dossier (over the menu)
            self.assertTrue(
                'ftw.mail.mail' not in [item.get('id') for item in menu_items])

            # a dossier in a dossier should called subdossier
            self.assertIn(
                self.labels.get('action_name'),
                [item.get('title') for item in menu_items])

            # Check title of addformular for a subdossier
            self.get_add_view(
                dossier_type, path=d1.absolute_url())

            self.assertEquals(
                self.labels.get(
                    'add_subdossier') in self.browser.contents, True)

            url = self.browser.url.split('/')[-1]
            self.assertTrue(url == '++add++%s' % dossier_type)

            # Check edit label
            d2 = self.create_dossier(dossier_type, subpath=d1.getId())
            self.get_edit_view(d2.absolute_url())
            self.assertEquals(
                self.labels.get(
                    'edit_subdossier') in self.browser.contents, True)

    def test_nesting_deepth(self):
        """Check the deepth of subdossiers. Normally we just can add a
        subdossier to a dossier and the subdossier must be the same
        dossier-type like the parent-dossier. Its not possible to add
        a subdossier to a subdossier
        """

        for dossier_type in self.dossier_types:
            dossiers = []
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

                self.browser.open(subdossier.absolute_url())
                # its possible to add a subdossier
                if i < self.deepth-1:
                    # Check link is enabled
                    self.assertEquals(
                        self.labels.get(
                            'action_name') in self.browser.contents, True)

                    # Check contenttype is allowed
                    self.assertIn(
                        dossier_type,
                        [fti.id for fti in subdossier.allowedContentTypes()])
                # its disallowed to add a subdossier
                else:
                    # Check link is disabled
                    self.assertNotEquals(
                        self.labels.get(
                            'action_name') in self.browser.contents, True)
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
        self.provideUtility(DummyVocabulary(),
                       name='opengever.ogds.base.ContactsVocabulary')

        for dossier_type, additional_searchable_attr in \
            self.dossier_types.items():

            dossier = self.create_dossier(dossier_type)
            wrapper = queryMultiAdapter(
                (dossier, self.portal.portal_catalog), IIndexableObject)
            #merge default and additional searchable attr
            searchable_attr = self.default_searchable_attr
            searchable_attr.update(additional_searchable_attr)

            for schemata in iterSchemata(dossier):
                for name, field in getFieldsInOrder(schemata):
                    value = searchable_attr.get(name, '')
                    if not value:
                        continue

                    field.set(field.interface(dossier), value)

                    # search value
                    if isinstance(value, list):
                        for v in value:
                            val = self.map_with_vocab(schemata, name, v)
                    # the field reference_number is handled special.
                    # the searchable text is set over an adapter whos
                    # return a reference-number. so we cant set the
                    # reference_number filed like the other attributes.
                    elif value == 'test_reference_number':
                        refNumb = getAdapter(dossier, IReferenceNumber)
                        val = refNumb.get_number()
                    # the filing_no is handled special.
                    # the searchable text is just set if the dossier is
                    # archived. So we bypass this
                    elif value == 'test_filing_no':
                        val = "GS-Filing 12345"
                        archived_dossier = IDossierMarker(dossier)
                        archived_dossier.filing_no = val
                    else:
                        val = self.map_with_vocab(schemata, name, value)

                    self.assertIn(
                        val.encode('utf-8'), wrapper.SearchableText)

                    # We pop the field if we found it to check at the
                    # end whether all attributes where found in the schema
                    searchable_attr.pop(name)

            # Test sequencenumber
            if searchable_attr.get(
                'sequence_number', '') == 'test_sequence_number':
                seqNumb = getUtility(ISequenceNumber)

                self.assertIn(
                    str(seqNumb.get_number(dossier)), wrapper.SearchableText)

                searchable_attr.pop('sequence_number')

        self.assertTrue(searchable_attr.values() == [])

    def provideUtility(self, component, name=''):
        sm = self.layer['portal'].getSiteManager()
        self._utilities.append(component)
        sm.registerUtility(component, name=name)

    def tearDown(self):
        """Cleanup the test-environment after each test
        """

        sm = self.layer['portal'].getSiteManager()
        for component in self._utilities:
            sm.unregisterUtility(component)

        # TODO: We need to reset the sequencenumber that other tests wont fail.
        # This implementation dont work.

        # Adjust the counter
        # new_counter_value = 0
        #         portal = self.layer['portal']
        #         ann = IAnnotations(portal)
        #         ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = PersistentDict()
        pass
