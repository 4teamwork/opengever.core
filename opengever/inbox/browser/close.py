from opengever.inbox import _
from opengever.task import _ as task_mf
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.util import change_task_workflow_state
from plone.supermodel import model
from plone.z3cform import layout
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema


# TODO: Use ISimpleResponseForm instead of define a same one.
class IForwardingCloseForm(model.Schema):
    """Special addresponse form for the forwarding close transition.
    Looks the same, but do something different.
    """

    text = schema.Text(
        title=task_mf('label_response', default="Response"),
        description=task_mf('help_response', default=""),
        required=False,
        )


class ForwardingCloseForm(Form):
    """Form for assigning task.
    """

    fields = Fields(IForwardingCloseForm)
    ignoreContext = True

    label = _(u'title_close_forwarding', u'Close orwarding')

    @button.buttonAndHandler(_(u'close', default='Close'), name='save')
    def handle_close(self, action):

        data, errors = self.extractData()
        if not errors:

            # close and store the forwarding in yearfolder
            change_task_workflow_state(
                self.context,
                'forwarding-transition-close',
                text=data.get('text'))

            IYearfolderStorer(self.context).store_in_yearfolder()

            return self.request.RESPONSE.redirect('.')

    @button.buttonAndHandler(task_mf(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ForwardingCloseFormView(layout.FormWrapper):

    form = ForwardingCloseForm
