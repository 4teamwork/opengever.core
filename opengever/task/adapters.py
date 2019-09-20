from opengever.base.protect import unprotected_write
from opengever.task.task import ITask
from persistent import Persistent
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IResponseContainer(Interface):
    """Deprecated interface. Used for old task response implementation.

    Remove as soon as upgrade MigrateOldTaskResponsesToResponsesNewImplementation
    """


class IResponse(Interface):
    """Deprecated interface. Used for old task response implementation.

    Remove as soon as upgrade MigrateOldTaskResponsesToResponsesNewImplementation
    have been installed on every deployment.
    """


@implementer(IResponseContainer)
@adapter(ITask)
class ResponseContainer(object):
    """Deprecated object. Used for old task response implementation.

    Remove as soon as upgrade MigrateOldTaskResponsesToResponsesNewImplementation
    """
    ANNO_KEY = 'poi.responses'

    def __init__(self, context):
        self.context = context
        annotations = unprotected_write(IAnnotations(self.context))
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[self.ANNO_KEY] = self.__mapping

    def __getitem__(self, i):
        i = int(i)
        return self.__mapping.__getitem__(i)


class Response(Persistent):
    """Deprecated object. Used for old task response implementation.

    Remove as soon as upgrade MigrateOldTaskResponsesToResponsesNewImplementation
    have been installed on every deployment.
    """
    implements(IResponse)
