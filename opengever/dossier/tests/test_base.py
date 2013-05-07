from DateTime import DateTime
from datetime import datetime, date
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import OPENGEVER_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAnnotations
import unittest2 as unittest

class TestDossierContainer(unittest.TestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_is_all_supplied(self):

        # dossiers wihtout a subdossier
        dossier = self._create_dossier(self.portal)
        self._create_document(dossier)
        self.assertTrue(dossier.is_all_supplied())

        # dossier containing docs and subdossiers
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self._create_document(dossier)
        self.assertFalse(dossier.is_all_supplied())

        # dossier containing tasks and subdossiers
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self._create_task(dossier)
        self.assertFalse(dossier.is_all_supplied())

        # dossier containing subdossier with objs
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self._create_task(subdossier)
        self._create_document(subdossier)
        self.assertTrue(dossier.is_all_supplied())

    def test_is_all_closed(self):
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self._create_task(dossier, review_state='task-state-cancelled')
        self._create_task(dossier, review_state='task-state-rejected')
        self._create_task(subdossier, review_state='task-state-tested-and-closed')
        self.assertTrue(dossier.is_all_closed())

        self._create_task(dossier, review_state='task-state-tested-in-progress')
        self.assertFalse(dossier.is_all_closed())

    def test_is_all_checked_in(self):
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self._create_document(dossier)
        self.assertTrue(dossier.is_all_checked_in())

        self._create_document(subdossier)
        self.assertTrue(dossier.is_all_checked_in())

        self._create_document(dossier, checked_out=TEST_USER_ID)
        self.assertFalse(dossier.is_all_checked_in())

        self._create_document(subdossier, checked_out=TEST_USER_ID)
        self.assertFalse(subdossier.is_all_checked_in())

    def test_possible_end_date_calculation(self):
        dossier = self._create_dossier(self.portal)
        self.assertEquals(dossier.earliest_possible_end_date(), None)

        self._create_dossier(dossier, end=datetime(2012, 02, 03))
        self.assertEquals(dossier.earliest_possible_end_date(), date(2012, 02, 03))

        self._create_dossier(dossier, end=datetime(2012, 02, 16))
        self.assertEquals(dossier.earliest_possible_end_date(), date(2012, 02, 16))

        self._create_document(dossier, document_date=date(2012, 02, 13))
        self.assertEquals(dossier.earliest_possible_end_date(), date(2012, 02, 16))

        self._create_document(dossier, document_date=date(2012, 02, 20))
        self.assertEquals(dossier.earliest_possible_end_date(), date(2012, 02, 20))

        subdossier = self._create_dossier(
            dossier, review_state='dossier-state-inactive')
        self._create_document(subdossier, document_date=date(2012, 03, 20))
        self.assertEquals(dossier.earliest_possible_end_date(), date(2012, 02, 20))

    def test_dossier_has_valid_startdate(self):
        dossier = self._create_dossier(self.portal)

        IDossier(dossier).start = date(2012, 02, 24)
        self.assertTrue(dossier.has_valid_startdate(),
                        "'%s' should be a valid startdate" % IDossier(dossier).start)

        IDossier(dossier).start = None
        self.assertFalse(dossier.has_valid_startdate(),
                         "None is not a valid startdate")

    def test_has_valid_enddate(self):
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        IDossier(subdossier).start = date(2012, 02, 24)
        self.assertTrue(dossier.has_valid_enddate())

        IDossier(dossier).end = date(2012, 02, 16)
        self.assertTrue(dossier.has_valid_enddate())

        self._create_document(dossier, document_date=date(2012, 02, 20))
        self.assertTrue(subdossier.has_valid_enddate())
        self.assertFalse(dossier.has_valid_enddate())

        IDossier(subdossier).end = date(2012, 02, 25)
        self._create_document(dossier, document_date=date(2012, 02, 25))
        self.assertTrue(subdossier.has_valid_enddate())

        IDossier(dossier).end = date(2012, 02, 24)
        self.assertFalse(dossier.has_valid_enddate())

        dossier = self._create_dossier(
            self.portal, start=date(2012, 2, 2), end=date(2012, 2, 1))
        self.assertFalse(dossier.has_valid_enddate())

    def test_get_parent_dossier(self):
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self.assertEquals(dossier.get_parent_dossier(), None)
        self.assertEquals(subdossier.get_parent_dossier(), dossier)

    def test_is_subdossier(self):
        dossier, subdossier = self._create_dossier(self.portal, with_sub=True)
        self.assertFalse(dossier.is_subdossier())
        self.assertTrue(subdossier.is_subdossier())

    def _create_dossier(self, context,
            with_sub=False, end=None, start=None, review_state=None):

        dossier = createContentInContainer(
            context,
            'opengever.dossier.businesscasedossier',
            title='Dossiers', checkConstraints=False)

        if end:
            IDossier(dossier).end = end

        if start:
            IDossier(dossier).start = start

        if review_state:
            wt = self.portal.portal_workflow
            wt.setStatusOf(
                'opengever_dossier_workflow',
                dossier,
                {'review_state': review_state,
                 'action': review_state,
                 'actor': TEST_USER_ID,
                 'time': DateTime(),
                 'comments': '', })

            dossier.reindexObject()

        if with_sub:
            subdossier = createContentInContainer(
                dossier,
                'opengever.dossier.businesscasedossier',
                title='Subdossier', checkConstraints=False)

            IDossier(subdossier).start = datetime.today().date()

            return dossier, subdossier

        return dossier

    def _create_document(self, context, checked_out=None, document_date=None):
        doc = createContentInContainer(
            context, 'opengever.document.document',
            title="Doc1", checkConstraints=False,
            document_date=document_date)

        if checked_out:
            IAnnotations(doc)[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = checked_out
            doc.reindexObject(idxs=['checked_out'])

        return doc

    def _create_task(self, context, responsible=TEST_USER_ID, review_state=None):

        task = createContentInContainer(
            context,
            'opengever.task.task',
            title="Task1", task_type='correction',
            checkConstraints=False)
        task.responsible = responsible

        if review_state:
            wt = self.portal.portal_workflow
            wt.setStatusOf(
                'opengever_task_workflow',
                task,
                {'review_state': review_state,
                 'action': review_state,
                 'actor': responsible,
                 'time': DateTime(),
                 'comments': '', })

        task.reindexObject()
        return task
