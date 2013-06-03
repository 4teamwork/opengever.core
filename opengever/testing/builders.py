from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobFile
from z3c.form.interfaces import IValue
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
from zope.schema import getFieldsInOrder
import transaction


def create(builder):
    return builder.create()

def Builder(name):
    if name == "dossier":
        return DossierBuilder(BuilderSession.instance())
    elif name == "document":
        return DocumentBuilder(BuilderSession.instance())
    elif name == "task":
        return TaskBuilder(BuilderSession.instance())
    elif name == "mail":
        return MailBuilder(BuilderSession.instance())
    elif name == "repository":
        return RepositoryBuilder(BuilderSession.instance())
    elif name == "contact":
        return ContactBuilder(BuilderSession.instance())
    else:
        raise ValueError("No Builder for %s" % name)


class BuilderSession(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.portal = None
        self.auto_commit = True

    @classmethod
    def instance(cls, *args, **kwgs):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(*args, **kwgs)
        return cls._instance


class DexterityBuilder(object):

    def __init__(self, session):
        self.session = session
        self.container = session.portal
        self.arguments = {"checkConstraints": False}
        self.set_default_values = False

    def within(self, container):
        self.container = container
        return self

    def titled(self, title):
        self.arguments["title"] = title
        return self

    def with_description(self, description):
        self.arguments["description"] = description
        return self

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def with_default_values(self):
        self.set_default_values = True
        return self

    def create(self, notify_events=True):
        self.before_create()
        obj = self.create_object()
        if self.set_default_values:
            self.set_defaults(obj)
        if notify_events:
            notify(ObjectCreatedEvent(obj))
            notify(ObjectAddedEvent(obj))

        self.after_create(obj)
        return obj

    def before_create(self):
        pass

    def after_create(self, obj):
        if self.session.auto_commit:
            transaction.commit()

    def set_defaults(self, obj):
        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if not field.get(field.interface(obj)):
                    default = queryMultiAdapter(
                        (obj, obj.REQUEST, None, field, None),
                        IValue,
                        name='default')
                    if default is not None:
                        default = default.get()
                    if default is None:
                        default = getattr(field, 'default', None)
                    if default is None:
                        try:
                            default = field.missing_value
                        except AttributeError:
                            pass
                    field.set(field.interface(obj), default)


class DossierBuilder(DexterityBuilder):

    def create_object(self):
        return createContentInContainer(self.container,
                                        'opengever.dossier.businesscasedossier',
                                        **self.arguments)


class DocumentBuilder(DexterityBuilder):

    def with_dummy_content(self):
        self.attach_file_containing("Test data")
        return self

    def attach_file_containing(self, content, name=u"test.doc"):
        self.attach(NamedBlobFile(data=content, filename=name))
        return self

    def attach(self, file_):
        self.arguments["file"] = file_
        return self

    def create_object(self):
        return createContentInContainer(self.container,
                                        'opengever.document.document',
                                        **self.arguments)


class TaskBuilder(DexterityBuilder):

    def __init__(self, session):
        super(TaskBuilder, self).__init__(session)
        self.transitions = []

    def create_object(self):
        return createContentInContainer(self.container,
                                        'opengever.task.task',
                                        **self.arguments)

    def in_progress(self):
        self.transitions.append('task-transition-open-in-progress')
        return self

    def after_create(self, obj):
        wtool = getToolByName(obj, 'portal_workflow')
        for transition in self.transitions:
            wtool.doActionFor(obj, transition)

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


class MailBuilder(DexterityBuilder):

    def with_dummy_message(self):
        self.with_message("foobar")
        return self

    def with_message(self, message, filename=u'testmail.eml'):
        file_ = NamedBlobFile(data=message, filename=filename)
        self.arguments["message"] = file_
        return self

    def create_object(self):
        return createContentInContainer(self.container,
                                        'ftw.mail.mail',
                                        **self.arguments)


class RepositoryBuilder(DexterityBuilder):

    def create_object(self):
        return createContentInContainer(self.container,
                                        'opengever.repository.repositoryfolder',
                                        **self.arguments)


class ContactBuilder(DexterityBuilder):

    def create_object(self):
        return createContentInContainer(self.container,
                                        'opengever.contact.contact',
                                        **self.arguments)
