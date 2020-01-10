from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.dexterity.content import Container


class WorkspaceBase(Container):

    def has_blocked_local_role_inheritance(self):
        return getattr(self, '__ac_local_roles_block__', False)

    def get_context_with_local_roles(self):
        """Returns the context which defines the local roles for the current
        context.
        """
        if not self.has_blocked_local_role_inheritance():
            return self.get_parent_with_local_roles()
        return self

    def get_parent_with_local_roles(self):
        parent = aq_parent(aq_inner(self))
        if parent.has_blocked_local_role_inheritance():
            return parent

        else:
            return parent.get_parent_with_local_roles()
