from Acquisition import aq_inner, aq_parent
from five.grok import subscribe
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.task import ITask
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class LocalRolesSetter(object):
    """Sets local roles.
    """

    def __init__(self, task):
        self.task = task

    def __call__(self, event):
        if not self.responsible:
            return
        self.set_roles_on_task()
        self.set_roles_on_distinct_parent()
        self.set_roles_on_related_items()

    @property
    def responsible(self):
        """Returns the responsible pricipal. This may be the userid
        of a user which is able to log in or the principal of a group,
        if a inbox was selected.
        """
        # cache information
        try:
            self._responsible
        except AttributeError:
            value = self.task.responsible
            info = getUtility(IContactInformation)

            if info.is_inbox(value):
                self._responsible = info.get_group_of_inbox(value)
            else:
                self._responsible = value

            if isinstance(self._responsible, unicode):
                self._responsible = self._responsible.encode('utf-8')

        return self._responsible

    def _add_local_roles(self, context, principal, roles):
        """Adds local roles to the context.
        `roles` example:
        {'peter': ('Reader', 'Editor')}
        """
        current_roles = dict(context.get_local_roles()).get(principal, ())
        new_roles = list(set(list(current_roles) + list(roles)))
        context.manage_setLocalRoles(principal, new_roles)
        context.reindexObjectSecurity()

    def set_roles_on_task(self):
        """Set local roles on task
        """
        self._add_local_roles(self.task, self.responsible, ('Editor',))

    def set_roles_on_distinct_parent(self):
        """Set local roles on the next parent which has a different
        content type.
        """
        context = self.task
        while context.Type() == self.task.Type():
            context = aq_parent(aq_inner(context))
        self._add_local_roles(context, self.responsible, ('Contributor', ))

    def set_roles_on_related_items(self):
        """Set local roles on related items (usually documents)
        """

        roles = ['Reader']
        if self.task.task_type_category == 'bidirectional_by_reference':
            roles.append('Editor')

        for item in getattr(self.task, 'relatedItems', []):
            self._add_local_roles(item.to_object, self.responsible, roles)


@subscribe(ITask, IObjectAddedEvent)
def set_roles_after_adding(context, event):
    LocalRolesSetter(context)(event)


@subscribe(ITask, IObjectModifiedEvent)
def set_roles_after_modifying(context, event):
    LocalRolesSetter(context)(event)
