from datetime import date
from dateutil.relativedelta import relativedelta
from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from ftw.builder.dexterity import DexterityBuilder
from opengever.base.behaviors.translated_title import TranslatedTitle
from opengever.base.oguid import Oguid
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.document import Document
from opengever.globalindex.handlers.task import sync_task
from opengever.mail.mail import OGMail
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Period
from opengever.task.interfaces import ISuccessorTaskController
from opengever.tasktemplates import INTERACTIVE_USERS
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import assets
from opengever.testing.builders.base import TEST_USER_ID
from opengever.testing.builders.translated import TranslatedTitleBuilderMixin
from opengever.trash.trash import ITrashable
from plone import api
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent


class DossierBuilder(DexterityBuilder):
    portal_type = 'opengever.dossier.businesscasedossier'

    def __init__(self, session):
        super(DossierBuilder, self).__init__(session)
        self.arguments['retention_period'] = 15

    def as_expired(self):
        """Resolves the dossier and set the end date so that the
        retention period is expired.
        """
        self.in_state('dossier-state-resolved')
        self.arguments['end'] = date.today() - relativedelta(
            years=self.arguments['retention_period'] + 1)

        return self


builder_registry.register('dossier', DossierBuilder)


class MeetingDossierBuilder(DossierBuilder):
    portal_type = 'opengever.meeting.meetingdossier'


builder_registry.register('meeting_dossier', MeetingDossierBuilder)


class TemplateFolderBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.dossier.templatefolder'


builder_registry.register('templatefolder', TemplateFolderBuilder)


class MeetingTemplateBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.meetingtemplate'


builder_registry.register('meetingtemplate', MeetingTemplateBuilder)


class ParagraphTemplateBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.paragraphtemplate'


builder_registry.register('paragraphtemplate', ParagraphTemplateBuilder)


class DossierTemplateBuilder(DexterityBuilder):
    portal_type = 'opengever.dossier.dossiertemplate'


builder_registry.register('dossiertemplate', DossierTemplateBuilder)


class InboxBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.inbox.inbox'


builder_registry.register('inbox', InboxBuilder)


class DocumentBuilder(DexterityBuilder):
    portal_type = 'opengever.document.document'
    _checked_out = None
    _trashed = False
    _is_shadow = False

    def __init__(self, session):
        super(DocumentBuilder, self).__init__(session)
        self.arguments['title'] = u'Testdokum\xe4nt'

    def with_dummy_content(self):
        self.attach_file_containing("Test data")
        return self

    def without_default_title(self):
        self.arguments.pop('title')
        return self

    def with_asset_file(self, filename):
        self.attach_file_containing(assets.load(filename), unicode(filename))
        return self

    def checked_out(self):
        return self.checked_out_by(TEST_USER_ID)

    def checked_out_by(self, userid):
        self._checked_out = userid
        return self

    def trashed(self):
        self._trashed = True
        return self

    def removed(self):
        self.review_state = Document.removed_state
        return self

    def as_shadow_document(self):
        self._is_shadow = True
        return self

    def after_create(self, obj):
        if self._checked_out:
            IAnnotations(obj)[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = self._checked_out
            obj.reindexObject(idxs=['checked_out'])

        if self._trashed:
            trasher = ITrashable(obj)
            trasher.trash()

        if self._is_shadow:
            obj.as_shadow_document()
            obj.reindexObject(idxs=["review_state"])

        super(DocumentBuilder, self).after_create(obj)

    def attach_file_containing(self, content, name=u"test.doc"):
        self.attach(NamedBlobFile(data=content, filename=name))
        return self

    def attach_archival_file_containing(self, content, name=u"test.pdf"):
        self.attach(NamedBlobFile(data=content, filename=name),
                    fieldname='archival_file')
        return self

    def attach(self, file_, fieldname="file"):
        self.arguments[fieldname] = file_
        return self

    def relate_to(self, documents):
        if not isinstance(documents, list):
            documents = [documents]

        self.arguments['relatedItems'] = documents
        return self


builder_registry.register('document', DocumentBuilder, force=True)


class SablonTemplateBuilder(DocumentBuilder):

    portal_type = 'opengever.meeting.sablontemplate'


builder_registry.register('sablontemplate', SablonTemplateBuilder)


class TaskBuilder(DexterityBuilder):
    portal_type = 'opengever.task.task'

    def __init__(self, session):
        super(TaskBuilder, self).__init__(session)
        self.transitions = []
        self.predecessor = None
        self._as_sequential_task = False
        self.arguments = {
            'responsible_client': 'org-unit-1',
            'responsible': TEST_USER_ID,
            'issuer': TEST_USER_ID}

    def in_progress(self):
        self.transitions.append('task-transition-open-in-progress')
        return self

    def after_create(self, obj):
        wtool = getToolByName(obj, 'portal_workflow')
        for transition in self.transitions:
            wtool.doActionFor(obj, transition)

        if self.predecessor:
            ISuccessorTaskController(obj).set_predecessor(self.predecessor)

        if self._as_sequential_task:
            alsoProvides(obj, IFromSequentialTasktemplate)

        super(TaskBuilder, self).after_create(obj)

    def relate_to(self, documents):
        if not isinstance(documents, list):
            documents = [documents, ]

        self.arguments['relatedItems'] = documents
        return self

    def bidirectional_by_reference(self):
        self.arguments['task_type'] = u'comment'
        return self

    def successor_from(self, predecessor):
        oguid = ISuccessorTaskController(predecessor).get_oguid()
        self.arguments['predecessor'] = oguid
        return self

    def change_workflow_state(self, obj):
        super(TaskBuilder, self).change_workflow_state(obj)
        sync_task(obj, None)

    def set_modification_date(self, obj):
        super(TaskBuilder, self).set_modification_date(obj)
        sync_task(obj, None)

    def as_sequential_task(self):
        self._as_sequential_task = True
        return self


builder_registry.register('task', TaskBuilder)


class ForwardingBuilder(TaskBuilder):

    portal_type = 'opengever.inbox.forwarding'


builder_registry.register('forwarding', ForwardingBuilder)


class MailBuilder(DexterityBuilder):
    portal_type = 'ftw.mail.mail'
    _trashed = False

    def with_dummy_message(self):
        self.with_message("foobar")
        return self

    def with_message(self, message, filename=u'testmail.eml'):
        file_ = NamedBlobFile(data=message, filename=filename)
        self.arguments["message"] = file_
        return self

    def with_dummy_original_message(self):
        file_ = NamedBlobFile(data='dummy', filename=u'dummy.msg')
        self.arguments["original_message"] = file_
        return self

    def with_asset_message(self, filename):
        self.with_message(assets.load(filename), unicode(filename))
        return self

    def trashed(self):
        self._trashed = True
        return self

    def removed(self):
        self.review_state = OGMail.removed_state
        return self

    def after_create(self, obj):
        if self._trashed:
            trasher = ITrashable(obj)
            trasher.trash()

        obj.update_filename()
        super(MailBuilder, self).after_create(obj)

    def set_missing_values_for_empty_fields(self, obj):
        """Fire ObjectCreatedEvent (again) to trigger setting of initial
        attribute values extracted from the message.
        """

        super(MailBuilder, self).set_missing_values_for_empty_fields(obj)

        notify(ObjectCreatedEvent(obj))


builder_registry.register('mail', MailBuilder)


class RepositoryBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.repository.repositoryfolder'


builder_registry.register('repository', RepositoryBuilder)


class ContactFolderBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.contact.contactfolder'


builder_registry.register('contactfolder', ContactFolderBuilder)


class ContactBuilder(DexterityBuilder):
    portal_type = 'opengever.contact.contact'


builder_registry.register('contact', ContactBuilder)


class RepositoryRootBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.repository.repositoryroot'

    def __init__(self, session):
        super(RepositoryRootBuilder, self).__init__(session)
        self._with_tree_portlet = False
        self.arguments = {
            'title_de': u'Ordnungssystem',
        }

    def with_tree_portlet(self):
        self._with_tree_portlet = True
        return self

    def after_create(self, obj):
        super(RepositoryRootBuilder, self).after_create(obj)
        if self._with_tree_portlet:
            create(Builder('tree portlet').for_root(obj))


builder_registry.register('repository_root', RepositoryRootBuilder)


class YearFolderbuilder(DexterityBuilder):
    portal_type = 'opengever.inbox.yearfolder'


builder_registry.register('yearfolder', YearFolderbuilder)


class InboxContainerBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.inbox.container'


builder_registry.register('inbox_container', InboxContainerBuilder)


class ProposalBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.proposal'

    def __init__(self, session):
        super(ProposalBuilder, self).__init__(session)
        self.arguments = {'title': 'Fooo',
                          'language': TranslatedTitle.FALLBACK_LANGUAGE,
                          'issuer': TEST_USER_ID}
        self._transition = None
        self._proposal_file_data = assets.load('empty.docx')
        self._also_return_submitted_proposal = False

    def with_proposal_file(self, data):
        self._proposal_file_data = data
        return self

    def before_create(self):
        if 'committee' in self.arguments:
            committee = self.arguments.pop('committee')
            if ICommittee.providedBy(committee):
                self.arguments['committee_oguid'] = Oguid.for_object(committee).id
            else:
                self.arguments['committee_oguid'] = committee.oguid.id

        super(ProposalBuilder, self).before_create()

    def after_create(self, obj):
        obj.create_proposal_document(
            title=obj.title_or_id(),
            filename=u'proposal_document.docx',
            data=self._proposal_file_data,
            content_type='application/vnd.openxmlformats'
            '-officedocument.wordprocessingml.document')

        if self._transition:
            api.content.transition(obj, self._transition)

        super(ProposalBuilder, self).after_create(obj)

    def create(self):
        proposal = super(ProposalBuilder, self).create()

        if self._also_return_submitted_proposal:
            submitted_proposal = self._traverse_submitted_proposal(proposal)
            return proposal, submitted_proposal

        return proposal

    def relate_to(self, *documents):
        return self.having(relatedItems=documents)

    def as_submitted(self):
        self._transition = 'proposal-transition-submit'
        return self

    def with_submitted(self):
        """Will return proposal and submitted proposal after creating."""

        self.as_submitted()
        self._also_return_submitted_proposal = True
        return self

    def _traverse_submitted_proposal(self, proposal):
        proposal_model = proposal.load_model()
        if not proposal_model.submitted_physical_path:
            return None

        path = proposal_model.submitted_physical_path.encode('utf-8')
        return api.portal.get().restrictedTraverse(path, default=None)


builder_registry.register('proposal', ProposalBuilder)


class CommitteeContainerBuilder(TranslatedTitleBuilderMixin, DexterityBuilder):
    portal_type = 'opengever.meeting.committeecontainer'


builder_registry.register('committee_container', CommitteeContainerBuilder)


class CommitteeBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.committee'

    def __init__(self, session):
        super(CommitteeBuilder, self).__init__(session)
        self.arguments = {'title': 'My Committee',
                          'group_id': u'org-unit-1_users'}
        self._with_default_period = False

    def link_with(self, repository_folder):
        self.arguments['repository_folder'] = repository_folder
        return self

    def after_create(self, obj):
        for fieldname in ('repository_folder',
                          'ad_hoc_template',
                          'paragraph_template',
                          'protocol_header_template',
                          'protocol_suffix_template',
                          'agenda_item_header_template',
                          'agenda_item_suffix_template',
                          'excerpt_header_template',
                          'excerpt_suffix_template',
                          'agendaitem_list_template',
                          'toc_template',
                          'allowed_proposal_templates',
                          'allowed_ad_hoc_agenda_item_templates'):
            self.arguments.pop(fieldname, None)

        obj.create_model(self.arguments, self.container)
        self.create_default_period(obj)

        super(CommitteeBuilder, self).after_create(obj)

    def with_default_period(self):
        self._with_default_period = True
        return self

    def create_default_period(self, obj):
        if not self._with_default_period:
            return

        today = date.today()
        create(Builder('period').within(obj).having(
              title=unicode(today.year),
              start=date(today.year, 1, 1),
              end=date(today.year, 12, 31)))


builder_registry.register('committee', CommitteeBuilder)


class PeriodBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.period'

    def __init__(self, session):
        super(PeriodBuilder, self).__init__(session)
        self.arguments['title'] = unicode(date.today().year)


builder_registry.register('period', PeriodBuilder)


class TaskTemplateFolderBuilder(DexterityBuilder):
    portal_type = 'opengever.tasktemplates.tasktemplatefolder'


builder_registry.register('tasktemplatefolder', TaskTemplateFolderBuilder)


class TaskTemplateBuilder(DexterityBuilder):
    portal_type = 'opengever.tasktemplates.tasktemplate'

    def __init__(self, session):
        super(TaskTemplateBuilder, self).__init__(session)

        self.arguments = {
            'responsible_client': INTERACTIVE_USERS,
            'responsible': 'current_user',
            'deadline': 5,
            'issuer': TEST_USER_ID}


builder_registry.register('tasktemplate', TaskTemplateBuilder)


class PrivateRootBuilder(DexterityBuilder):
    portal_type = 'opengever.private.root'


builder_registry.register('private_root', PrivateRootBuilder)


class PrivateFolderBuilder(DexterityBuilder):
    portal_type = 'opengever.private.folder'


builder_registry.register('private_folder', PrivateFolderBuilder)


class PrivateDossierBuilder(DossierBuilder):
    portal_type = 'opengever.private.dossier'


builder_registry.register('private_dossier', PrivateDossierBuilder)


class DispositionBuilder(DexterityBuilder):
    portal_type = 'opengever.disposition.disposition'

    def __init__(self, session):
        super(DispositionBuilder, self).__init__(session)
        # OfferedDossiersValidator is broken when this is import is in
        # module scope.
        from opengever.disposition.disposition import title_default
        self.arguments['title'] = title_default()


builder_registry.register('disposition', DispositionBuilder)


class ProposalTemplateBuilder(DocumentBuilder):

    portal_type = 'opengever.meeting.proposaltemplate'

    def __init__(self, *args, **kwargs):
        super(ProposalTemplateBuilder, self).__init__(*args, **kwargs)
        self.with_dummy_content()


builder_registry.register('proposaltemplate', ProposalTemplateBuilder)


class WorkspaceRootBuilder(DexterityBuilder):
    portal_type = 'opengever.workspace.root'


builder_registry.register('workspace_root', WorkspaceRootBuilder)


class WorkspaceBuilder(DexterityBuilder):
    portal_type = 'opengever.workspace.workspace'


builder_registry.register('workspace', WorkspaceBuilder)


class WorkspaceFolderBuilder(DexterityBuilder):
    portal_type = 'opengever.workspace.folder'


builder_registry.register('workspace folder', WorkspaceFolderBuilder)


class ToDoBuilder(DexterityBuilder):
    portal_type = 'opengever.workspace.todo'


builder_registry.register('todo', ToDoBuilder)


class ToDoListBuilder(DexterityBuilder):
    portal_type = 'opengever.workspace.todolist'


builder_registry.register('todolist', ToDoListBuilder)
