from Acquisition import aq_inner
from Acquisition import aq_parent
from five.grok import subscribe
from opengever.globalindex.handlers.task import sync_task
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.task import ITask
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class LocalRolesSetter(object):
    """Sets local roles.
    """

    def __init__(self, task):
        self.task = task
        self._inbox_group_id = None

    def __call__(self, event):
        self.event = event
        if not self.responsible:
            return
        self.set_roles_on_task()
        self.globalindex_reindex_task()
        self.set_roles_on_related_items()
        self.set_roles_on_distinct_parent()

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
                self._responsible = info.get_groupid_of_inbox(value)
            else:
                self._responsible = value

            if isinstance(self._responsible, unicode):
                self._responsible = self._responsible.encode('utf-8')

        return self._responsible

    @property
    def inbox_group_id(self):
        if self._inbox_group_id is None:
            self._inbox_group = self.task.get_responsible_org_unit().inbox_group().groupid
        return self._inbox_group

    def is_inboxgroup_agency_active(self):
        return get_current_org_unit().is_inboxgroup_agency_active

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
        if self.is_inboxgroup_agency_active() and self.inbox_group_id:
            self._add_local_roles(self.task, self.inbox_group_id, ('Editor',))

    def globalindex_reindex_task(self):
        """We need to reindex the task in globalindex. This was done
        already with an earlier event handler - but we have just changed
        the roles which are indexed too (allowed users).
        """
        sync_task(self.task, self.event)

    def set_roles_on_distinct_parent(self):
        """Set local roles on the next parent which has a different
        content type.
        """

        context = self.task
        while context.Type() == self.task.Type():
            context = aq_parent(aq_inner(context))
        self._add_local_roles(context, self.responsible, ('Contributor', ))
        if self.is_inboxgroup_agency_active() and self.inbox_group_id:
            self._add_local_roles(context, self.inbox_group_id, ('Contributor', ))

    def set_roles_on_related_items(self):
        """Set local roles on related items (usually documents)
        """

        roles = ['Reader']
        if self.task.task_type_category == 'bidirectional_by_reference':
            roles.append('Editor')

        for item in getattr(self.task, 'relatedItems', []):
            self._add_local_roles(item.to_object, self.responsible, roles)
            if self.is_inboxgroup_agency_active() and self.inbox_group_id:
                self._add_local_roles(item.to_object, self.inbox_group_id, roles)


@subscribe(ITask, IObjectAddedEvent)
def set_roles_after_adding(context, event):
    LocalRolesSetter(context)(event)


@subscribe(ITask, IObjectModifiedEvent)
def set_roles_after_modifying(context, event):
    LocalRolesSetter(context)(event)
