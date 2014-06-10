from Products.CMFCore.utils import getToolByName
from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.task.interfaces import ISuccessorTaskController
from opengever.trash.trash import ITrashable
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
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

    def checked_out_by(self, userid):
        self.checked_out = userid
        return self

    def trashed(self):
        self._trashed = True
        return self

    def after_create(self, obj):
        if self.checked_out:
            IAnnotations(obj)[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = self.checked_out

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


builder_registry.register('document', DocumentBuilder, force=True)


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

builder_registry.register('task', TaskBuilder)


class ForwardingBuilder(TaskBuilder):

    portal_type = 'opengever.inbox.forwarding'


builder_registry.register('forwarding', ForwardingBuilder)


class MailBuilder(DexterityBuilder):
    portal_type = 'ftw.mail.mail'

    def with_dummy_message(self):
        self.with_message("foobar")
        return self

    def with_message(self, message, filename=u'testmail.eml'):
        file_ = NamedBlobFile(data=message, filename=filename)
        self.arguments["message"] = file_
        return self


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
