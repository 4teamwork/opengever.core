from five import grok
from opengever.base.clipboard import Clipboard
from opengever.dossier.behaviors.dossier import IDossierMarker
from ZODB.POSException import ConflictError
from zope.interface import Interface


class IsPastingAllowedView(grok.View):
    """A view to determine if pasting objects is supposed to be allowed on a
    particular context.
    Used in the available expression of the object_buttons 'paste' action.
    """

    grok.name('is_pasting_allowed')
    grok.context(Interface)
    grok.require('zope2.View')

    disabled_types = ('opengever.dossier.templatedossier',
                      'opengever.contact.contactfolder',
                      'ftw.mail.mail')

    @property
    def allowed_content_types(self):
        """Returns a tuple of allowed portal types for the container as
        per the container's FTI.

        XXX: This should be extended to consider
             1) Per-context constrained dossier types (special dossiers)
             2) The constraint that dossiers can't be added in non-leaf nodes
                of the repository
        """
        container_fti = self.context.getTypeInfo()
        return container_fti.allowed_content_types

    def is_allowed(self):
        """Perform the necessary checks to determine whether pasting is
        allowed / possible on the current context.
        """
        # Check whether pasting is allowed at all for the container type
        if self.context.portal_type in self.disabled_types:
            return False

        # XXX implement me in a more object oriented manner, i.e. by
        # implementing `is_pasting_allowed` for all our content types.
        if IDossierMarker.providedBy(self.context):
            if not self.context.is_open():
                return False

        objs = Clipboard(self.request).get_objs()
        if not objs:
            # Clipboard empty
            return False

        # Check whether there's an object in the clipboard whose type
        # is not allowed to be added to the container
        for obj in objs:
            if obj.portal_type not in self.allowed_content_types:
                return False

        return True

    def render(self):
        allowed = False
        # This view is called on *every request*. It's therefore critical
        # that it doesn't raise any exceptions.
        # (One example of an exception that could be raised is a KeyError
        # if a document is first copied, and after that the same document
        # is then moved, and the restrictedTraverse fails)
        try:
            allowed = self.is_allowed()
        except ConflictError:
            raise
        except Exception:
            pass
        return allowed
