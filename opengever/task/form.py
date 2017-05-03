from copy import deepcopy
from five import grok
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task.activities import TaskAddedActivity
from opengever.task.activities import TaskReassignActivity
from opengever.task.task import IAddTaskSchema
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.task.util import update_reponsible_field_data
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import dexterity
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


REASSIGN_TRANSITION = 'task-transition-reassign'


# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.


class TaskAddForm(dexterity.AddForm):
    grok.name('opengever.task.task')

    def __init__(self, *args, **kwargs):
        super(TaskAddForm, self).__init__(*args, **kwargs)
        self.instance_schema = IAddTaskSchema

    @property
    def schema(self):
        return self.instance_schema

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
        super(TaskAddForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one orgunit configured.
        if not ogds_service().has_multiple_org_units():
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")

    def createAndAdd(self, data):
        created = []
        if isinstance(data['responsible'], basestring):
            data['responsible'] = [data['responsible']]

        for responsible in data['responsible']:
            task_payload = deepcopy(data)
            task_payload['responsible'] = responsible
            update_reponsible_field_data(task_payload)

            created.append(self._create_task(task_payload))

        self._set_immediate_view(created)
        return created

    def _create_task(self, task_payload):

        view = self.context.restrictedTraverse('++add++opengever.task.task')
        task_form = view.form_instance
        task_form.instance_schema = ITask

        task_form.updateFieldsFromSchemata()
        task_form.updateWidgets()

        task = task_form.create(task_payload)
        notify(ObjectCreatedEvent(task))
        task_form.add(task)

        activity = TaskAddedActivity(task, self.request, self.context)
        activity.record()
        return task

    def _set_immediate_view(self, created):
        """The default behavior implemented by the dexterity add form is
        circumvented by this form. If there's only one task the immediate_view
        of the task fti is respected. If there is more than one task, a
        differen TaskRedirector implementation is used."""

        if len(created) == 1:
            task = created[0]
            fti = getUtility(IDexterityFTI, name=self.portal_type)
            if fti.immediate_view:
                self.immediate_view = "{0}/{1}/{2}".format(
                    self.context.absolute_url(),
                    task.id, fti.immediate_view,)
            else:
                self.immediate_view = "{0}/{1}".format(
                    self.context.absolute_url(),
                    task.id)
        else:
            if ITask.providedBy(self.context):
                redirect_to = '{0}#overview'.format(self.context.absolute_url())
            else:
                redirect_to = '{0}#tasks'.format(self.context.absolute_url())

            self.immediate_view = redirect_to


class TaskEditForm(dexterity.EditForm):
    """The standard dexterity EditForm with the following customizations:

     - Require the Edit Task permission
     - Omit `responsible` and `responsible_client` fields and adjust field
       description for single orgunit deployments
     - Records reassign activity when the responsible has changed.
    """

    grok.context(ITask)
    grok.require('opengever.task.EditTask')

    def update(self):
        super(TaskEditForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one client configured.
        if not ogds_service().has_multiple_org_units():
            self.groups[0].widgets['responsible_client'].mode = HIDDEN_MODE
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")

    def applyChanges(self, data):
        """Records reassign activity when the responsible has changed.
        Also update the responsible_cliend and responsible user
        """
        update_reponsible_field_data(data)

        if self.is_reassigned(data):
            response = self.add_reassign_response(data)
            changes = super(TaskEditForm, self).applyChanges(data)
            TaskReassignActivity(self.context, self.context.REQUEST, response).record()
        else:
            changes = super(TaskEditForm, self).applyChanges(data)

        return changes

    def is_reassigned(self, data):
        if self.context.responsible != data.get('responsible') or \
           self.context.responsible_client != data.get('responsible_client'):
            return True

        return False

    def add_reassign_response(self, data):
        return add_simple_response(
            self.context,
            text=None,
            field_changes=(
                (ITask['responsible'], data.get('responsible')),
                (ITask['responsible_client'],
                 data.get('responsible_client')),),
            transition=REASSIGN_TRANSITION)
