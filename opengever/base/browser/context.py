from plone.app.layout.globals.context import ContextState
from plone.app.layout.globals.interfaces import IContextState
from plone.memoize.view import memoize
from zope.interface import implements


class WrapperContextState(ContextState):

    implements(IContextState)

    @memoize
    def object_title(self):
        return self.context.get_title()
