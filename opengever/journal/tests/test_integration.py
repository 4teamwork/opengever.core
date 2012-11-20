from DateTime import DateTime
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from OFS.event import ObjectWillBeMovedEvent, ObjectWillBeAddedEvent
from opengever.document.events import \
    ObjectCheckedOutEvent, ObjectCheckedInEvent, \
    ObjectCheckoutCanceledEvent, ObjectRevertedToVersion
from opengever.dossier.events import ParticipationCreated, ParticipationRemoved
from opengever.dossier.behaviors.participation import Participation
from opengever.journal.testing import OPENGEVER_JOURNAL_INTEGRATION_TESTING
from opengever.trash.trash import TrashedEvent, UntrashedEvent
from opengever.sharing.events import LocalRolesAcquisitionBlocked, \
    LocalRolesAcquisitionActivated, LocalRolesModified
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import ActionSucceededEvent
from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent import ObjectMovedEvent
from zope.event import notify
from zope.i18n import translate
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import unittest2 as unittest
from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFields
from zope.component import getUtility
from opengever.mail.events import DocumentSent
from plone.registry.interfaces import IRegistry
from opengever.ogds.base.interfaces import IClientConfiguration
from zope.intid.interfaces import IIntIds


class TestOpengeverJournalGeneral(unittest.TestCase):

    layer = OPENGEVER_JOURNAL_INTEGRATION_TESTING

    def test_integration_repository_events(self):
        """ Trigger every event of a repo at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']

        repo_root = createContentInContainer(
            portal, 'opengever.repository.repositoryroot', 'root')
        repo = createContentInContainer(
            repo_root, 'opengever.repository.repositoryfolder', 'r1')

        # Local roles Aquisition Blocked-Event
        notify(
            LocalRolesAcquisitionBlocked(repo, ))

        # Check
        self.check_annotation(
            repo_root,
            action_type='Local roles Aquisition Blocked',
            action_title='Local roles aquistion blocked at %s.' % (
                repo.title_or_id()))

        # Local roles Aquisition Activated-Event
        notify(
            LocalRolesAcquisitionActivated(repo, ))

        # Check
        self.check_annotation(
            repo_root,
            action_type='Local roles Aquisition Activated',
            action_title='Local roles aquistion activated at %s.' % (
                repo.title_or_id()))

        # Local roles Modified
        notify(
            LocalRolesModified(repo, 'old roles',
                (
                ['catman', ['Owner']],
                ['ratman', ['Owner', 'Reader']],
                ['test_user', ['Reader', 'Publisher']],
                )
            ))

        # CheckLocalRolesModified
        self.check_annotation(
            repo_root,
            action_type='Local roles modified',
            action_title='Local roles modified at %s.' % (
                repo.title_or_id()),
            comment='ratman: sharing_dossier_reader; test_user: ' \
                'sharing_dossier_reader, sharing_dossier_publisher')

    def test_integration_dossier_events(self):
        """ Trigger every event of a dossier at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']


        # Add-Event
        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        self.check_object_added(
            dossier,
            'Dossier added',
            'Dossier added: %s' % dossier.title_or_id(), )

        # Modified-Event
        notify(ObjectModifiedEvent(dossier))

        # Check
        self.check_annotation(dossier,
                              action_type='Dossier modified',
                              action_title='Dossier modified: %s' % (
                                dossier.title_or_id()))

        # Get the workflow for the dossier to test the ActionSucceededEvent
        wftool = getToolByName(dossier, 'portal_workflow')
        workflow = wftool.get('simple_publication_workflow')

        # Action-Succeeded-Event
        notify(
            ActionSucceededEvent(dossier, workflow, 'publish', 'published', ))

        # Check
        self.check_annotation(
            dossier,
            action_type='Dossier state changed',
            action_title='Dossier state changed to published')

        # Local roles Aquisition Blocked-Event
        notify(
            LocalRolesAcquisitionBlocked(dossier, ))

        # Check
        self.check_annotation(
            dossier,
            action_type='Local roles Aquisition Blocked',
            action_title='Local roles aquistion blocked.')

        # Local roles Aquisition Activated-Event
        notify(
            LocalRolesAcquisitionActivated(dossier, ))

        # Check
        self.check_annotation(
            dossier,
            action_type='Local roles Aquisition Activated',
            action_title='Local roles aquistion activated.')

        # Local roles Modified
        notify(
            LocalRolesModified(dossier, 'old roles',
                (
                ['catman', ['Owner']],
                ['ratman', ['Owner', 'Reader']],
                ['test_user', ['Reader', 'Publisher']],
                )
            ))

        # CheckLocalRolesModified
        self.check_annotation(
            dossier,
            action_type='Local roles modified',
            action_title='Local roles modified.',
            comment='ratman: sharing_dossier_reader; test_user: ' \
                'sharing_dossier_reader, sharing_dossier_publisher')

    def test_integration_templatedossier_event(self):

        portal = self.layer['portal']

        templatedossier = createContentInContainer(
            portal, 'opengever.dossier.templatedossier', 'templates')

        # Local roles Modified
        notify(
            LocalRolesModified(templatedossier, 'old roles',
                (
                ['catman', ['Owner']],
                ['ratman', ['Owner', 'Reader']],
                ['test_user', ['Reader', 'Editor']],
                )
            ))

        # CheckLocalRolesModified
        self.check_annotation(
            templatedossier,
            action_type='Local roles modified',
            action_title='Local roles modified.',
            comment='ratman: sharing_reader; test_user: ' \
                'sharing_reader, sharing_editor')


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

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = u'Test'
        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        # Add-Event
        document = createContentInContainer(
            dossier, 'opengever.document.document', 'd1', title=u'Doc\xfcment')

        self.check_object_added(
            document,
            'Document added',
            'Document added: %s' % document.title_or_id(),
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
        notify(ObjectRevertedToVersion(document, '', ''))
        self.assertTrue(length == self.get_journal_length(document))

        # Object Reverted-To-Version-Event
        notify(ObjectRevertedToVersion(document, 'v1', 'v1'))
        self.check_document_revertedtoversion(document)

        notify(DocumentSent(dossier, TEST_USER_ID, 'test@test.ch', 'test mail', 'Mymessage', [document]))
        self.check_document_sent(dossier, document)

    def test_integration_task_events(self):
        """ Trigger every event of a task at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        # Add-Event
        task = createContentInContainer(
            dossier, 'opengever.task.task', 'd1')

        self.check_annotation(
            dossier,
            action_type='Task added',
            action_title='Task added: %s' % task.title_or_id(),
            check_entry=-2, )

        # Modified-Event
        notify(ObjectModifiedEvent(task))
        self.check_annotation(
            dossier,
            action_type='Task modified',
            action_title='Task modified: %s' % task.title_or_id(), )



    def test_integration_trashed_events(self):
        """ Trigger every event of trashing objects
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        # Create object to put it in the trash
        document = createContentInContainer(
            dossier, 'opengever.document.document', 'd1')

        # Trash-Event
        notify(TrashedEvent(document))

        self.check_annotation(
            document,
            action_type='Object moved to trash',
            action_title='Object moved to trash: %s' % (
                document.title_or_id()), )
        self.check_annotation(
            dossier,
            action_type='Object moved to trash',
            action_title='Object moved to trash: %s' % (
                document.title_or_id()), )

        # Untrash-Event
        notify(UntrashedEvent(document))
        self.check_annotation(
            document,
            action_type='Object restore',
            action_title='Object restore: %s' % (
                document.title_or_id()), )
        self.check_annotation(
            dossier,
            action_type='Object restore',
            action_title='Object restore: %s' % (
                document.title_or_id()), )

    def test_integration_participation_events(self):
        """ Trigger every event of a participation at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']
        participant = Participation('ratman', ['held', 'manager'])

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        # Participation-Created-Event
        notify(ParticipationCreated(dossier, participant))
        self.check_annotation(
            dossier,
            action_type='Participant added',
            action_title='Participant added: %s with roles %s' % (
                participant.contact, ', '.join(participant.roles)), )

        # Participation-Removed-Event
        notify(ParticipationRemoved(dossier, participant))
        self.check_annotation(
            dossier,
            action_type='Participant removed',
            action_title='Participant removed: %s' % (
                participant.contact), )

    def test_integration_mail_events(self):
        """ Trigger every event of a mail at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
        schema = fti.lookupSchema()
        field_type = getFields(schema)['message']._type
        msgtxt = 'Subject: mail-test\n'

        mail = createContentInContainer(
            dossier, 'ftw.mail.mail',
            message=field_type(data=msgtxt,
                contentType=u'message/rfc822', filename=u'attachment.txt'))

        # The journal of a mail is always on the parents dossier and not
        # on the mail
        self.check_annotation(
            dossier,
            action_type='Mail added',
            action_title='Mail added: %s' % mail.title_or_id(),
            check_entry=-2, )

    def test_integration_object_events(self):
        """ Trigger every event of a objec at least one times
        and check the journalentries.
        """
        portal = self.layer['portal']

        dossier1 = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')
        dossier2 = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd2')

        document = createContentInContainer(
            dossier1, 'opengever.document.document', 'doc1', title='Document')

        notify(ObjectMovedEvent(
            document,
            dossier1,
            'oldName',
            dossier2,
            'newName', ))
        self.check_annotation(
            dossier1,
            action_type='Object moved',
            action_title='Object moved: %s' % document.title_or_id(), )

        notify(ObjectWillBeMovedEvent(
            document,
            dossier1,
            'oldName',
            dossier2,
            'newName', ))
        self.check_annotation(
                dossier1,
                action_type='Object cut',
                action_title='Object cut: %s' % document.title_or_id(), )

        # Here we don't have a journal-entry
        length = self.get_journal_length(dossier1)
        notify(ObjectWillBeAddedEvent(
            document,
            dossier2,
            'newName', ))
        self.assertTrue(length == self.get_journal_length(dossier1))

    # Helpers
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
        self.assertEquals(comment, journal.get('comments'))
        self.assertEquals(actor, journal.get('actor'))
        self.assertEquals(time, journal.get('time').Date())
        self.assertEquals(action_type, journal.get('action').get('type'))
        self.assertEquals(
            action_title, translate(journal.get('action').get('title')))

    def check_object_added(
        self, obj, action_type='', action_title='', parent=None):
        """ Check the journal after adding a object
        """
        self.check_annotation(obj,
                              action_type=action_type,
                              action_title=action_title)

        if parent:
            self.check_annotation(parent,
                                  action_type=action_type,
                                  action_title=action_title,
                                  check_entry=-2, )

    def check_document_modified(self, obj, parent, mode):
        """ Check the journal after modifying a document
        """

        if mode == 'file':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='Changed file')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='Changed file of document %s' % (
                    obj.title_or_id()), )

        elif mode == 'meta':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='Changed metadata')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='Changed metadata of document %s' % (
                    obj.title_or_id()), )

        elif mode == 'file_meta':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='Changed file and metadata')
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='Changed file and metadata of document %s' % (
                    obj.title_or_id()), )

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
            action_title='Document checked out',
            comment=comment, )

    def check_document_checkedin(self, obj, comment):
        """ Check the journal after checked in
        """

        self.check_annotation(
            obj,
            action_type='Document checked in',
            action_title='Document checked in',
            comment=comment, )

    def check_document_checkoutcanceled(self, obj):
        """ Check the journal after checkout canceled
        """

        self.check_annotation(
            obj,
            action_type='Canceled document checkout',
            action_title='Canceled document checkout')

    def check_document_revertedtoversion(self, obj):
        """ Check the journal after reverting
        """

        self.check_annotation(
            obj,
            action_type='Reverted document file',
            action_title='Reverte document file to version v%s' % (
                "1"))

    def check_document_sent(self, obj, doc):
        id_util = getUtility(IIntIds)
        intid = id_util.queryId(doc)
        self.check_annotation(
            obj,
            action_type='Document Sent',
            action_title=u'Document sent by Mail: test mail',
            actor=TEST_USER_ID,
            comment='Attachments: <span><a href="./@@resolve_oguid?oguid=Test:'+str(
                intid)+'">'+ doc.Title()+
            '</a></span> | Receivers: test@test.ch |\
                    Message: Mymessage',)
