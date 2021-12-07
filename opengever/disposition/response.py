from opengever.base.response import IResponse
from opengever.base.response import Response
from persistent.list import PersistentList
from zope.interface import implements


class IDispositionResponse(IResponse):
    """Marker interface for disposition responses."""


class DispositionResponse(Response):

    implements(IDispositionResponse)

    def __init__(self, *args, **kwargs):
        super(DispositionResponse, self).__init__(*args, **kwargs)
        self.dossiers = PersistentList()
