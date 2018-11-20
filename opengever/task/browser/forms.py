from opengever.task import is_private_task_feature_enabled
from opengever.task.activities import TaskAddedActivity
from opengever.task.activities import TaskReassignActivity
from opengever.task.task import IAddTaskSchema
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.task.util import update_reponsible_field_data
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityFTI
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


class TaskAddForm(DefaultAddForm):

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

        # hide tasktemplate_position field and insert value
        # if it was passed by.
        position = self.request.get('position')
        additional_group = [group for group in self.groups
                            if group.__name__ == u'additional'][0]
        if position:
            additional_group.widgets['tasktemplate_position'].value = position

        additional_group.widgets['tasktemplate_position'].mode = HIDDEN_MODE

        if not is_private_task_feature_enabled():
            common_group = next(
                group for group in self.groups if group.__name__ == u'common')
            common_group.widgets['is_private'].mode = HIDDEN_MODE

    def createAndAdd(self, data):
        created = []
        if isinstance(data['responsible'], basestring):
            data['responsible'] = [data['responsible']]

        all_responsible_users = data['responsible']
        for responsible in all_responsible_users:
            data['responsible'] = responsible
            update_reponsible_field_data(data)
            created.append(self._create_task(data))

        # Restore responsible in data
        data['responsible'] = all_responsible_users

        # Set tasktemplate order and move to planned state if it's part
        # of a sequential process
        if IFromSequentialTasktemplate.providedBy(self.context):
            position = data['tasktemplate_position']
            if not position:
                position = len(self.context.get_tasktemplate_order())

            for task in created:
                self.context.add_task_to_tasktemplate_order(position, task)

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


class TaskAddView(DefaultAddView):
    form = TaskAddForm


class TaskEditForm(DefaultEditForm):
    """The standard dexterity EditForm with the following customizations:

     - Require the Edit Task permission
     - Records reassign activity when the responsible has changed.
    """

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
            transition=REASSIGN_TRANSITION, supress_events=True)
