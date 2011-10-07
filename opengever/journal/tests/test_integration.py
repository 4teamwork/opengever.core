from DateTime import DateTime
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from opengever.document.events import ObjectCheckedOutEvent, ObjectCheckedInEvent, ObjectCheckoutCanceledEvent, ObjectRevertedToVersion
from opengever.journal.testing import OPENGEVER_JOURNAL_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import ActionSucceededEvent
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import unittest2 as unittest


class TestFtwJournalGeneral(unittest.TestCase):

    layer = OPENGEVER_JOURNAL_INTEGRATION_TESTING

    def test_integration_dossier_events(self):
        """ Trigger every event of a dossier at least one times
        and check the journalentries.
        """

        portal = self.layer['portal']

        # Add-Event
        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier','d1')

        self.check_object_added(
            dossier,
            'Dossier added',
            'label_dossier_added', )

        # Modified-Event
        notify(ObjectModifiedEvent(dossier))

        # Check
        self.check_annotation(dossier,
                              action_type='Dossier modified',
                              action_title='label_dossier_modified')

        # Get the workflow for the dossier to test the ActionSucceededEvent
        wftool = getToolByName(dossier, 'portal_workflow')
        workflow = wftool.get('simple_publication_workflow')

        # Action-Succeeded-Event
        notify(ActionSucceededEvent(dossier, workflow, 'publish', 'published', ))

        # Check
        self.check_annotation(dossier,
                              action_type='Dossier state changed',
                              action_title='Dossier state changed to published')

    def test_integration_document_events(self):
        """ Trigger every event of a document at least one times
        and check the journalentries.

        Attention: we always have to check the parent.
        If we add a document to a dossier, the dossier is modified.
        So on the dossiers journal there are two new entries, one for the new
        document and one for the changed dossier. We just have to check the
        entry of the new document on the dossiers journal
        """
        portal = self.layer['portal']
        comment = 'my comment'

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier','d1')

        # Add-Event
        document = createContentInContainer(
            dossier, 'opengever.document.document','d1')
        self.check_object_added(
            document,
            'Document added',
            'label_document_added',
            dossier)

        # Modified-Event - nothing changed
        length_document = self.get_journal_length(document)
        length_dossier = self.get_journal_length(dossier)

        notify(ObjectModifiedEvent(document))

        self.assertTrue(length_document == self.get_journal_length(document))
        self.assertTrue(length_dossier == self.get_journal_length(dossier))

        # Modified-Event - file changed
        notify(ObjectModifiedEvent(document, Attributes(Interface, 'file')))
        self.check_document_modified(document, dossier, 'file')

        # Modified-Event - meta changed
        notify(ObjectModifiedEvent(document, Attributes(Interface, 'meta')))
        self.check_document_modified(document, dossier, 'meta')

        # Modified-Event - file and meta changed
        notify(ObjectModifiedEvent(
            document, Attributes(Interface, 'file', 'meta')))
        self.check_document_modified(document, dossier, 'file_meta')

        # Get the workflow for the document to test the ActionSucceededEvent
        wftool = getToolByName(document, 'portal_workflow')
        workflow = wftool.get('simple_publication_workflow')

        # Action-Succeeded-Event with skipped transaction
        length = self.get_journal_length(document)
        notify(ActionSucceededEvent(
            document, workflow, 'check_out', 'checked_out', ))
        self.assertTrue(length == self.get_journal_length(document))

        # Action-Succeeded-Event
        notify(ActionSucceededEvent(
            document, workflow, 'publish', 'published', ))
        self.check_document_actionsucceeded(document)

        # Object Checked-Out-Event
        notify(ObjectCheckedOutEvent(document, comment))
        self.check_document_checkedout(document, comment)

        # Object Checked-In-Event
        notify(ObjectCheckedInEvent(document, comment))
        self.check_document_checkedin(document, comment)

        # Object Checked-Out-Canceled-Event
        notify(ObjectCheckoutCanceledEvent(document))
        self.check_document_checkoutcanceled(document)

        # Object Reverted-To-Version-Event with fail
        length = self.get_journal_length(document)
        notify(ObjectRevertedToVersion(document, '',''))
        self.assertTrue(length == self.get_journal_length(document))

        # Object Reverted-To-Version-Event
        notify(ObjectRevertedToVersion(document, 'v1','v1'))
        self.check_document_revertedtoversion(document)

    def test_integration_task_events(self):
        """ Trigger every event of a task at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier','d1')

        # Add-Event
        task = createContentInContainer(
            dossier, 'opengever.task.task','d1')

        self.check_object_added(
            task,
            'Task added',
            'label_task_added',
            dossier, )


    def test_integration_participation_events(self):
        """ Trigger every event of a participation at least one times
        and check the journalentries.
        """
        pass

    def test_integration_mail_events(self):
        """ Trigger every event of a mail at least one times
        and check the journalentries.
        """
        pass

    def test_integration_object_events(self):
        """ Trigger every event of a objec at least one times
        and check the journalentries.
        """
        pass

    def get_journal_length(self, obj):
        """ Get the lenght of the journal
        """
        return len(IAnnotations(
            obj, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
                JOURNAL_ENTRIES_ANNOTATIONS_KEY))

    def check_annotation(self,
                         obj,
                         action_type='',
                         action_title='',
                         actor=TEST_USER_ID,
                         comment='',
                         check_entry=-1, ):
        """ Check the annotations for the right entries.
        """
        time = DateTime().Date()

        journal = IAnnotations(
            obj, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
                JOURNAL_ENTRIES_ANNOTATIONS_KEY)[check_entry]

        self.assertTrue(comment == journal.get('comments'))
        self.assertTrue(actor == journal.get('actor'))
        self.assertTrue(time == journal.get('time').Date())
        self.assertTrue(action_type == journal.get('action').get('type'))
        self.assertTrue(action_title == journal.get('action').get('title'))

    def check_object_added(self, obj, action_type='', action_title='', parent=None):
        """ Check the journal after adding a document
        """
        self.check_annotation(obj,
                              action_type=action_type,
                              action_title=action_title)

        if parent:
            self.check_annotation(parent,
                                  action_type=action_type,
                                  action_title=action_type,
                                  check_entry=-2, )

    def check_document_modified(self, obj, parent, mode):
        """ Check the journal after modifying a document
        """

        if mode == 'file':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='label_document_file_modified')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='label_document_file_modified__parent',
                check_entry=-1, )

        elif mode == 'meta':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='label_document_metadata_modified')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='label_document_metadata_modified__parent',
                check_entry=-1, )

        elif mode == 'file_meta':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='label_document_file_and_metadata_modified')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='label_document_file_and_metadata_modified__parent',
                check_entry=-1, )

    def check_document_actionsucceeded(self, obj):
        """ Check the journal after changing portal state
        """

        self.check_annotation(
            obj,
            action_type='Document state changed',
            action_title='Document state changed to published')

    def check_document_checkedout(self, obj, comment):
        """ Check the journal after checked out
        """

        self.check_annotation(
            obj,
            action_type='Document checked out',
            action_title='label_document_checkout',
            comment=comment, )

    def check_document_checkedin(self, obj, comment):
        """ Check the journal after checked in
        """

        self.check_annotation(
            obj,
            action_type='Document checked in',
            action_title='label_document_checkin',
            comment=comment, )

    def check_document_checkoutcanceled(self, obj):
        """ Check the journal after checkout canceled
        """

        self.check_annotation(
            obj,
            action_type='Canceled document checkout',
            action_title='label_document_checkout_cancel')

    def check_document_revertedtoversion(self, obj):
        """ Check the journal after reverting
        """

        self.check_annotation(
            obj,
            action_type='Reverted document file',
            action_title='label_document_file_reverted')


        # @grok.subscribe(ITask, IObjectAddedEvent)
        # def task_added(context, event):
        #
        # @grok.subscribe(ITask, IObjectModifiedEvent)
        # def task_modified(context, event):
        #
        # @grok.subscribe(IJournalizable, ITrashedEvent)
        # def document_trashed(context, event):
        #
        # @grok.subscribe(IJournalizable, IUntrashedEvent)
        # def document_untrashed(context, event):
        #
        # @grok.subscribe(IDossierMarker, IParticipationCreated)
        # def participation_created(context, event):
        #
        # @grok.subscribe(IDossierMarker, IParticipationRemoved)
        # def participation_removed(context, event):
        #
        # @grok.subscribe(IMail, IObjectAddedEvent)
        # def mail_added(context, event):
        #
        # @grok.subscribe(IDexterityContent, IObjectMovedEvent)
        # def object_moved(context, event):
        #
        # @grok.subscribe(IDexterityContent,IObjectWillBeMovedEvent)
        # def object_will_be_moved(context, event):
