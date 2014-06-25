from AccessControl import getSecurityManager
from DateTime import DateTime
from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.actor import Actor
from opengever.task.response_description import ResponseDescription
from opengever.task.task import ITask
from persistent import Persistent
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.interfaces import UnaddableError
from zope.component import getUtility
from zope.event import notify
from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute("Text of this response")
    rendered_text = Attribute("Rendered text (html) for caching")
    transition = Attribute('ID of perfomed transition - if any')
    changes = Attribute("Changes made to the issue in this response.")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this response was made.")
    type = Attribute("Type of response (additional/clarification/reply).")
    mimetype = Attribute("Mime type of the response.")
    relatedItems = Attribute('Related Items')
    added_object = Attribute('Relation to an added object')
    successor_oguid = Attribute('OGUID releation to a successor')

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(grok.Adapter):
    grok.implements(IResponseContainer)
    grok.context(ITask)
    ANNO_KEY = 'poi.responses'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[self.ANNO_KEY] = self.__mapping

    def __contains__(self, key):
        '''See interface IReadContainer

        Taken from zope.app.container.btree.

        Reimplement this method, since has_key() returns the key if available,
        while we expect True or False.

        >>> c = ResponseContainer()
        >>> "a" in c
        False
        >>> c["a"] = 1
        >>> "a" in c
        True
        >>> "A" in c
        False
        '''
        return key in self.__mapping

    has_key = __contains__

    def __getitem__(self, i):
        i = int(i)
        return self.__mapping.__getitem__(i)

    def __delitem__(self, item):
        self.__mapping.__delitem__(item)

    def __len__(self):
        return self.__mapping.__len__()

    def __setitem__(self, i, y):
        self.__mapping.__setitem__(i, y)

    def append(self, item):
        self.__mapping.append(item)

    def remove(self, item):
        self.__mapping.remove(item)

    def add(self, item):
        if not IResponse.providedBy(item):
            raise UnaddableError(self, item,
                                 "IResponse interface not provided.")
        self.append(item)
        id = str(len(self))
        event = ObjectAddedEvent(item, newParent=self.context, newName=id)
        notify(event)

    def delete(self, id):
        # We need to fire an ObjectRemovedEvent ourselves here because
        # self[id].__parent__ is not exactly the same as self, which
        # in the end means that __delitem__ does not fire an
        # ObjectRemovedEvent for us.
        #
        # Also, now we can say the oldParent is the issue instead of
        # this adapter.
        event = ObjectRemovedEvent(self[id], oldParent=self.context,
                                   oldName=id)
        self.remove(self[id])
        notify(event)


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text):
        self.__parent__ = self.__name__ = None
        self.text = text
        self.changes = PersistentList()
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId()
        self.date = DateTime()
        self.type = 'additional'
        self.mimetype = ''
        self.rendered_text = None
        self.relatedItems = ()
        self.added_object = None
        self.successor_oguid = None
        self.transition = None
        self._description = None

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id=id,
            name=name,
            before=before,
            after=after)
        self.changes.append(delta)

    def creator_link(self):
        return Actor.lookup(self.creator).get_link()

    def css_class(self):
        return self.get_description().css_class

    def msg(self):
        return self.get_description().msg()

    def get_succesor(self):
        self.successor_oguid
        try:
            self.successor_oguid
        except AttributeError:
            return None

        if self.successor_oguid:
            query = getUtility(ITaskQuery)
            return query.get_task_by_oguid(self.successor_oguid)
        else:
            return None

    def get_description(self):
        return ResponseDescription.get(self)

    def get_change(self, field_name):
        changes = [change for change in self.changes if change.get('id') == field_name]
        if changes:
            return changes[0]
        return {}

    def get_added_objects(self):
        """ Returns two lists of docs, subtasks
        """
        try:
            self.added_object
        except AttributeError:
            return [], []

        # .. and sometimes it may be empty.
        if not self.added_object:
            return [], []

        # Support for multiple added objects
        if hasattr(self.added_object, '__iter__'):
            relations = self.added_object
        else:
            relations = [self.added_object]

        docs = []
        subtasks = []
        for rel in relations:
            obj = rel.to_object
            if ITask.providedBy(obj):
                subtasks.append(obj)
            else:
                docs.append(obj)

        return docs, subtasks


class EmptyExporter(object):

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir, root=False):
        return
