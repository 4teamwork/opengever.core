from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from opengever.document.checkout import handlers
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.app.testing import setRoles, TEST_USER_ID
from zope.component import provideUtility
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import json
import unittest2 as unittest


class DummyContactVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        # overwrite the contactsvocabulary utitlity with
        dummy_vocab = SimpleVocabulary(
            [SimpleTerm(value=u'contact:hugo.boss', title='Hugo Boss'),
             SimpleTerm(value=u'contact:james.bond', title='James Bond'), ])

        return dummy_vocab


class DummyUsersVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        # overwrite the contactsvocabulary utitlity with
        dummy_vocab = SimpleVocabulary(
            [SimpleTerm(value=u'chuck.norris', title='Chuck Norris'),
             SimpleTerm(value=u'brad.pitt', title='Brad Pitt'), ])

        return dummy_vocab


TEST_CREATED_MAPPING = {
    7: datetime(2011, 1, 11, 10, 10),
    4: datetime(2011, 2, 11, 10, 10),
    3: datetime(2011, 3, 11, 10, 10),
    9: datetime(2011, 4, 11, 10, 10),
    11: datetime(2011, 5, 11, 10, 10),
    6: datetime(2011, 6, 11, 10, 10),
    1: datetime(2011, 7, 11, 10, 10),
    5: datetime(2011, 8, 11, 10, 10),
    2: datetime(2011, 9, 11, 10, 10),
    12: datetime(2011, 10, 11, 10, 10),
    8: datetime(2011, 11, 11, 10, 10),
    10: datetime(2011, 12, 11, 10, 10),
    }


class TestViewsIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def setUp(self):
        # disable create_inital_version handler for og.documents
        # otherwise we have some savepoints problems with the sqlite db
        handlers.MIGRATION = True

        super(TestViewsIntegration, self).setUp()

    def tearDown(self):
        # disable create_inital_version handler for og.documents
        # otherwise we have some savepoints problems with the sqlite db
        handlers.MIGRATION = False

        super(TestViewsIntegration, self).tearDown()

    def test_overview(self):

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Reviewer', 'Manager'])

        # fake the vocabularies
        provideUtility(
            DummyContactVocabulary(),
            name='opengever.ogds.base.ContactsVocabulary')

        provideUtility(
            DummyUsersVocabulary(),
            name='opengever.ogds.base.UsersVocabulary')

        # create testing dossier
        portal.invokeFactory(
            'opengever.dossier.businesscasedossier', 'dossier_overview_test')
        dossier = portal['dossier_overview_test']
        IDossier(dossier).responsible = 'chuck.norris'

        # create test objects
        self._create_objects(
            dossier, 'opengever.dossier.businesscasedossier', 'Subdossier', 7)

        self._create_objects(
            dossier, 'opengever.document.document', 'Document', 12)

        self._create_objects(
            dossier, 'opengever.task.task', 'Task', 7)

        # create also two testmails
        self._create_objects(
            dossier, 'ftw.mail.mail', 'Mail', 2)

        #updated manually the modification date to avoid conflicts with the documents
        dossier.get('mail-1').setModificationDate(datetime(2011, 8, 11, 20, 10))
        dossier.get('mail-1').reindexObject(idxs=['modified'])

        dossier.get('mail-2').setModificationDate(datetime(2011, 6, 11, 20, 10))
        dossier.get('mail-2').reindexObject(idxs=['modified'])


        # get the overview
        overview = dossier.unrestrictedTraverse('tabbedview_view-overview')

        subdossier = dossier.get('subdossier-1')
        subdossier_overview = subdossier.unrestrictedTraverse(
            'tabbedview_view-overview')

        #check boxes
        self.assertEquals(
            [[box.get('id') for box in boxes] for boxes in overview.boxes()],
            [
                ['subdossiers', 'participants'],
                ['newest_tasks', ],
                ['newest_documents', 'description']]
            )

        self.assertEquals(
            [[box.get('id') for box in boxes]
             for boxes in subdossier_overview.boxes()],
            [
                ['newest_tasks', ],
                ['participants', ],
                ['newest_documents', 'description']
            ]
            )

        #check subdossiers (numbers, order, maindossier isn't included)
        subdossier_titles = [a.Title for a in overview.subdossiers()]
        self.assertEquals(len(subdossier_titles), 5)
        self.assertTrue('Dossier' not in subdossier_titles)
        self.assertEquals(
            subdossier_titles,
            ['Subdossier 2', 'Subdossier 5', 'Subdossier 1',
             'Subdossier 6', 'Subdossier 3'])

        #check tasks(numbers, order)
        task_titles = [a.Title for a in overview.tasks()]
        self.assertEquals(len(task_titles), 5)
        self.assertEquals(
            task_titles,
            ['Task 2', 'Task 5', 'Task 1', 'Task 6', 'Task 3'])

        #check documents(numbers, order)
        document_titles = [a.get('Title') for a in overview.documents()]
        self.assertEquals(len(document_titles), 10)

        self.assertEquals(
            document_titles,
            [u'Document 10', u'Document 8', u'Document 12', u'Document 2',
             u'no_subject', u'Document 5', u'Document 1',  u'no_subject',
             u'Document 6', u'Document 11', ])

        # check description
        dossier.description = 'Simple test description'
        self.assertEquals(overview.description(), 'Simple test description')

        # check participation box
        # (should include the responsible of the dossier)
        participations = [s.get('Title') for s in  overview.sharing()]
        self.assertTrue('chuck.norris' in participations)

    def test_jsonviews(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Reviewer', 'Manager'])

        # remove all existing dossiers
        dossiers = portal.portal_catalog(
            object_provides=IDossierMarker.__identifier__,
            is_subdossier=False)

        for brain in dossiers:
            try:
                aq_parent(brain.getObject()).manage_delObjects(brain.getId)
            except Exception:
                import pdb; pdb.set_trace()

        # create test objects
        self._create_objects(
            portal, 'opengever.dossier.businesscasedossier', 'Testdossier', 7)

        wft = getToolByName(portal, 'portal_workflow')

        wft.doActionFor(
            portal.get('testdossier-3'), 'dossier-transition-resolve')
        wft.doActionFor(
            portal.get('testdossier-5'), 'dossier-transition-resolve')

        # call the json view
        json_data = portal.unrestrictedTraverse('list-open-dossiers-json')()

        # and check the json result
        objs = json.loads(json_data)

        self.assertEquals(objs[0].get('url'), u'http://nohost/plone/testdossier-1')
        self.assertEquals(objs[0].get('path'), u'testdossier-1')
        self.assertEquals(objs[0].get('review_state'), u'dossier-state-active')
        self.assertEquals(objs[0].get('title'), u'Testdossier 1')
        self.assertEquals(objs[0].get('reference_number'), u'OG / 7')

        # only active dossiers are included in the result
        titles = [o.get('title') for o in objs]
        self.assertTrue('Testdossier 3' not in titles)
        self.assertTrue('Testdossier 5' not in titles)

    def _create_objects(self, context, type, title, number):
        for i in range(1, number + 1):
            context.invokeFactory(
                type,
                '%s-%s' % (title.lower(), i),
                title='%s %s' % (title, i))

            obj = context.get('%s-%s' % (title.lower(), i))
            obj.setModificationDate(TEST_CREATED_MAPPING.get(i))
            obj.reindexObject(idxs=['modified'])
