from Acquisition import aq_base
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


class TaskSqlSyncer(object):

    def __init__(self, obj, event):
        self.obj = obj
        self.event = event

        if not self.is_uninstalling_plone():
            self.admin_unit_id = get_current_admin_unit().id()
            self.current_org_unit_id = get_current_org_unit().id()
            self.sequence_number = self.obj.get_sequence_number()
            self.obj_id = self.get_object_id()
            self.task_query = Session.query(Task).filter_by(
                admin_unit_id=self.admin_unit_id, int_id=self.obj_id)

    def is_uninstalling_plone(self):
        return IObjectRemovedEvent.providedBy(self.event) \
            and IPloneSiteRoot.providedBy(self.event.object)

    def get_object_id(self):
        intids = getUtility(IIntIds)
        try:
            int_id = intids.getId(self.obj)
        except KeyError:
            try:
                # In some case (remote task updating etc)
                # only the base_object provides an intid.
                int_id = intids.getId(aq_base(self.obj))
            except KeyError:
                # The intid event handler didn' create a intid for this object
                # yet. The event will be fired again after creating the id.
                return None
        return int_id

    def get_sql_task(self):
        task = self.task_query.first()
        if task is None:
            task = Task(self.obj_id, self.admin_unit_id,
                        issuing_org_unit=self.current_org_unit_id,
                        sequence_number=self.sequence_number)
            Session.add(task)
        return task

    def sync(self):
        if self.is_uninstalling_plone():
            return

        if self.obj_id is None:
            return

        task = self.get_sql_task()
        task.sync_with(self.obj)


def sync_task(obj, event):
    """Index the given task in opengever.globalindex.
    """
    TaskSqlSyncer(obj, event).sync()
