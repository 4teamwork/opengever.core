from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from OFS.event import ObjectWillBeAddedEvent
from OFS.event import ObjectWillBeMovedEvent
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.document.events import FileCopyDownloadedEvent
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.events import ObjectCheckedOutEvent
from opengever.document.events import ObjectCheckoutCanceledEvent
from opengever.document.events import ObjectRevertedToVersion
from opengever.dossier.behaviors.participation import Participation
from opengever.dossier.events import ParticipationCreated, ParticipationRemoved
from opengever.journal.tests.utils import get_journal_entry
from opengever.journal.tests.utils import get_journal_length
from opengever.mail.events import DocumentSent
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.sharing.events import LocalRolesModified
from opengever.trash.trash import TrashedEvent, UntrashedEvent
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import ActionSucceededEvent
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import ObjectMovedEvent
import unittest as unittest


class TestOpengeverJournalGeneral(unittest.TestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestOpengeverJournalGeneral, self).setUp()

        create(Builder('fixture').with_all_unit_setup())
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

    def test_integration_repository_events(self):
        """ Trigger every event of a repo at least one times
        and check the journalentries.
        """
        repo_root, repo = create(Builder('repository_tree'))

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
            LocalRolesModified(
                repo, 'old roles',
                (['catman', ['Owner']],
                 ['ratman', ['Owner', 'Reader']],
                 ['test_user', ['Reader', 'Publisher']])
            ))

        # CheckLocalRolesModified
        self.check_annotation(
            repo_root,
            action_type='Local roles modified',
            action_title='Local roles modified at %s.' % (
                repo.title_or_id()),
            comment='ratman: sharing_dossier_reader; test_user: '
                    'sharing_dossier_reader, sharing_dossier_publisher')

    def test_integration_dossier_events(self):
        """ Trigger every event of a dossier at least one times
        and check the journalentries.
        """

        # Add-Event
        dossier = create(Builder('dossier'))

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
            LocalRolesModified(
                dossier, 'old roles',
                (['catman', ['Owner']],
                 ['ratman', ['Owner', 'Reader']],
                 ['test_user', ['Reader', 'Publisher']])
            ))

        # CheckLocalRolesModified
        self.check_annotation(
            dossier,
            action_type='Local roles modified',
            action_title='Local roles modified.',
            comment='ratman: sharing_dossier_reader; test_user: '
                    'sharing_dossier_reader, sharing_dossier_publisher')

    def test_integration_document_events(self):
        """ Trigger every event of a document at least one times
        and check the journalentries.

        Attention: we always have to check the parent.
        If we add a document to a dossier, the dossier is modified.
        So on the dossiers journal there are two new entries, one for the new
        document and one for the changed dossier. We just have to check the
        entry of the new document on the dossiers journal
        """
        comment = 'my comment'

        dossier = create(Builder('dossier'))

        # Add-Event
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content()
                          .titled(u'Doc\xfcment'))

        self.check_object_added(
            document,
            'Document added',
            'Document added: %s' % document.title_or_id(),
            dossier)

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
        length = get_journal_length(document)
        notify(ObjectRevertedToVersion(document, '', ''))
        self.assertTrue(length == get_journal_length(document))

        # Object Reverted-To-Version-Event
        notify(ObjectRevertedToVersion(document, 'v1', 'v1'))
        self.check_document_revertedtoversion(document)

        # Object Sent Document Event
        notify(DocumentSent(dossier, TEST_USER_ID, 'test@example.com',
                            'test mail', 'Mymessage', [document]))
        self.check_document_sent(dossier, document)

        # Object downloaded file-copy Event
        notify(FileCopyDownloadedEvent(document))
        self.check_document_copy_downloaded(document)

    def test_integration_task_events(self):
        """ Trigger every event of a task at least one times
        and check the journalentries.
        """

        dossier = create(Builder('dossier'))

        # Add-Event
        task = create(Builder('task').within(dossier))

        self.check_annotation(
            dossier,
            action_type='Task added',
            action_title='Task added: %s' % task.title_or_id(),
            check_entry=-1, )

        # Modified-Event
        notify(ObjectModifiedEvent(task))
        self.check_annotation(
            dossier,
            action_type='Task modified',
            action_title='Task modified: %s' % task.title_or_id(), )

    def test_integration_trashed_events(self):
        """ Trigger every event of trashing objects
        """

        dossier = create(Builder('dossier'))

        # Create object to put it in the trash
        document = create(Builder('document').within(dossier))

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
            action_title='Object restored: %s' % (
                document.title_or_id()), )
        self.check_annotation(
            dossier,
            action_type='Object restore',
            action_title='Object restored: %s' % (
                document.title_or_id()), )

    def test_integration_participation_events(self):
        """ Trigger every event of a participation at least one times
        and check the journalentries.
        """

        participant = Participation('ratman', ['held', 'manager'])

        dossier = create(Builder('dossier'))

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

        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        # The journal of a mail is on the parent dossier as well as
        # on the mail itself
        self.check_annotation(
            dossier,
            action_type='Document added',
            action_title='Document added: %s' % mail.title_or_id(),
            check_entry=-1)

        self.check_annotation(
            mail,
            action_type='Document added',
            action_title='Document added: %s' % mail.title_or_id(),
            check_entry=-1)

    def test_integration_object_events(self):
        """ Trigger every event of a objec at least one times
        and check the journalentries.
        """

        dossier1 = create(Builder('dossier'))
        dossier2 = create(Builder('dossier'))

        document = create(Builder('document')
                          .within(dossier1)
                          .titled(u'Document'))
        document2 = create(Builder('document')
                           .within(dossier2)
                           .titled(u'Document'))

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

        # Test that a normal ObjectAddedEvent does not result in an object
        # moved journal entry.
        notify(ObjectAddedEvent(document2))
        entry1 = get_journal_entry(dossier2, entry=-1)
        entry2 = get_journal_entry(dossier2, entry=-2)
        self.assertTrue(entry1.get('action').get('type') != 'Object moved')
        self.assertTrue(entry2.get('action').get('type') != 'Object moved')

        notify(ObjectWillBeMovedEvent(
            document,
            dossier1,
            'oldName',
            dossier2,
            'newName', ))
        self.check_annotation(
            dossier1,
            action_type='Object cut',
            action_title='Object cut: %s' % document.title_or_id())

        # Here we don't have a journal-entry
        length = get_journal_length(dossier1)
        notify(ObjectWillBeAddedEvent(
            document,
            dossier2,
            'newName', ))
        self.assertTrue(length == get_journal_length(dossier1))

    # Helpers
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

        journal = get_journal_entry(obj, entry=check_entry)
        self.assertEquals(comment, journal.get('comments'))
        self.assertEquals(actor, journal.get('actor'))
        self.assertEquals(time, journal.get('time').Date())
        self.assertEquals(action_type, journal.get('action').get('type'))
        self.assertEquals(
            action_title, translate(journal.get('action').get('title')))

    def check_object_added(self, obj, action_type='',
                           action_title='', parent=None):
        """ Check the journal after adding a object
        """
        self.check_annotation(obj,
                              action_type=action_type,
                              action_title=action_title)

        if parent:
            self.check_annotation(parent,
                                  action_type=action_type,
                                  action_title=action_title,
                                  check_entry=-1, )

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

        elif mode == 'public_trial':
            self.check_annotation(
                obj,
                action_type='Document modified',
                action_title='Changed metadata',
                check_entry=-2)
            self.check_annotation(
                obj,
                action_type='Public trial modified',
                action_title=u'Public trial changed to "unchecked".',
                check_entry=-1)
            self.check_annotation(
                parent,
                action_type='Document modified',
                action_title='Changed metadata of document %s' % (
                    obj.title_or_id()), )

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
        # Testing on __dummy_unit_id__ from
        # `opengever.ogds.base.ou_selector.NullOrg`') is just a temporary
        # solution and will be adjusted when reworking the oguid functionality.
        self.check_annotation(
            obj,
            action_type='Document Sent',
            action_title=u'Document sent by Mail: test mail',
            actor=TEST_USER_ID,
            comment=(
                'Attachments: <span>'
                '<a href="{}">{}</a>'
                '</span> | Receivers: test@example.com |'
                ' Message: Mymessage'.format(doc.absolute_url(), doc.Title()))
            )

    def check_document_copy_downloaded(self, obj):
        title = u'Download copy current version (0)'
        self.check_annotation(
            obj,
            action_type='File copy downloaded',
            action_title=title,
            actor=TEST_USER_ID)
