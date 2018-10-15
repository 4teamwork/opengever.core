from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.clipboard import Clipboard
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.private.interfaces import IPrivateContainer
from plone import api
from Products.Five import BrowserView
from ZODB.POSException import ConflictError


class IsPastingAllowedView(BrowserView):
    """A view to determine if pasting objects is supposed to be allowed on a
    particular context.
    Used in the available expression of the object_buttons 'paste' action.
    """

    disabled_types = ('opengever.dossier.templatefolder',
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
        # Check whether the user has Copy or Move on the context
        if not api.user.has_permission('Copy or Move', obj=self.context):
            return False

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

        return self.validate_private_folder_pasting(objs)

    def is_content_in_private_folder(self, obj):
        parent = aq_parent(aq_inner(obj))
        return IPrivateContainer.providedBy(parent)

    def validate_private_folder_pasting(self, objs):
        """Check that only private content is pasted to private containers.
        """
        if IPrivateContainer.providedBy(self.context):
            return all(
                [self.is_content_in_private_folder(obj) for obj in objs])

        return True

    def __call__(self):
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
