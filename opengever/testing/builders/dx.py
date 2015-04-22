from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.document import Document
from opengever.globalindex.handlers.task import sync_task
from opengever.mail.mail import OGMail
from opengever.meeting.proposal import Proposal
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import assets
from opengever.testing.builders.base import TEST_USER_ID
from opengever.trash.trash import ITrashable
from plone import api
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class DossierBuilder(DexterityBuilder):
    portal_type = 'opengever.dossier.businesscasedossier'

builder_registry.register('dossier', DossierBuilder)


class TemplateDossierBuilder(DexterityBuilder):
    portal_type = 'opengever.dossier.templatedossier'

builder_registry.register('templatedossier', TemplateDossierBuilder)


class InboxBuilder(DexterityBuilder):
    portal_type = 'opengever.inbox.inbox'

builder_registry.register('inbox', InboxBuilder)


class DocumentBuilder(DexterityBuilder):
    portal_type = 'opengever.document.document'
    checked_out = None
    _trashed = False

    def with_dummy_content(self):
        self.attach_file_containing("Test data")
        return self

    def with_asset_file(self, filename):
        self.attach_file_containing(assets.load(filename), unicode(filename))
        return self

    def checked_out_by(self, userid):
        self.checked_out = userid
        return self

    def trashed(self):
        self._trashed = True
        return self

    def removed(self):
        self.review_state = Document.removed_state
        return self

    def after_create(self, obj):
        if self.checked_out:
            IAnnotations(obj)[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = self.checked_out
            obj.reindexObject()

        if self._trashed:
            trasher = ITrashable(obj)
            trasher.trash()

        super(DocumentBuilder, self).after_create(obj)

    def attach_file_containing(self, content, name=u"test.doc"):
        self.attach(NamedBlobFile(data=content, filename=name))
        return self

    def attach(self, file_):
        self.arguments["file"] = file_
        return self

    def relate_to(self, documents):
        if not isinstance(documents, list):
            documents = [documents]

        intids = getUtility(IIntIds)
        self.arguments['relatedItems'] = [
            RelationValue(intids.getId(doc)) for doc in documents]
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
        self.arguments = {
            'responsible_client': 'client1',
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

        super(TaskBuilder, self).after_create(obj)

    def relate_to(self, documents):
        if not isinstance(documents, list):
            documents = [documents, ]

        intids = getUtility(IIntIds)
        self.arguments['relatedItems'] = [
            RelationValue(intids.getId(doc)) for doc in documents]
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

        super(MailBuilder, self).after_create(obj)

builder_registry.register('mail', MailBuilder)


class RepositoryBuilder(DexterityBuilder):
    portal_type = 'opengever.repository.repositoryfolder'

    def titled(self, title):
        self.arguments["effective_title"] = title
        return self

builder_registry.register('repository', RepositoryBuilder)


class ContactFolderBuilder(DexterityBuilder):
    portal_type = 'opengever.contact.contactfolder'

builder_registry.register('contactfolder', ContactFolderBuilder)


class ContactBuilder(DexterityBuilder):
    portal_type = 'opengever.contact.contact'

builder_registry.register('contact', ContactBuilder)


class RepositoryRootBuilder(DexterityBuilder):
    portal_type = 'opengever.repository.repositoryroot'

builder_registry.register('repository_root', RepositoryRootBuilder)


class YearFolderbuilder(DexterityBuilder):
    portal_type = 'opengever.inbox.yearfolder'

builder_registry.register('yearfolder', YearFolderbuilder)


class InboxContainerBuilder(DexterityBuilder):
    portal_type = 'opengever.inbox.container'

builder_registry.register('inbox_container', InboxContainerBuilder)


class ProposalBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.proposal'

    def __init__(self, session):
        super(ProposalBuilder, self).__init__(session)
        self.arguments = {'title': 'Fooo'}
        self.model_arguments = None
        self._submitted = False

    def before_create(self):
        self.arguments, self.model_arguments = Proposal.partition_data(
            self.arguments)

    def after_create(self, obj):
        obj.create_model(self.model_arguments, self.container)

        if self._submitted:
            obj.execute_transition('pending-submitted')

        super(ProposalBuilder, self).after_create(obj)

    def relate_to(self, *documents):
        intids = getUtility(IIntIds)
        related_documents = [RelationValue(intids.getId(document))
                             for document in documents]
        return self.having(relatedItems=related_documents)

    def as_submitted(self):
        self._submitted = True
        return self

builder_registry.register('proposal', ProposalBuilder)


class SubmittedProposalBuilder(object):

    def __init__(self, session):
        self.session = session
        self.proposal = None

    def submitting(self, proposal):
        self.proposal = proposal
        return self

    def create(self):
        assert self.proposal, 'source proposal must be specified'

        self.proposal.execute_transition('pending-submitted')
        proposal_model = self.proposal.load_model()
        path = proposal_model.submitted_physical_path.encode('utf-8')
        return api.portal.get().restrictedTraverse(path)

builder_registry.register('submitted_proposal', SubmittedProposalBuilder)


class CommitteeContainerBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.committeecontainer'

    relation_fields = [
        'pre_protocol_template', 'protocol_template', 'excerpt_template']

    def before_create(self):
        """Make sure relations are set up correctly."""

        super(CommitteeContainerBuilder, self).before_create()

        intids = getUtility(IIntIds)
        for field_name in self.relation_fields:
            obj = self.arguments.pop(field_name, None)
            if obj:
                self.arguments[field_name] = RelationValue(intids.getId(obj))

builder_registry.register('committee_container', CommitteeContainerBuilder)


class CommitteeBuilder(DexterityBuilder):
    portal_type = 'opengever.meeting.committee'

    def __init__(self, session):
        super(CommitteeBuilder, self).__init__(session)
        self.arguments = {'title': 'My Committee'}

    def after_create(self, obj):
        obj.create_model(self.arguments, self.container)
        super(CommitteeBuilder, self).after_create(obj)

builder_registry.register('committee', CommitteeBuilder)
