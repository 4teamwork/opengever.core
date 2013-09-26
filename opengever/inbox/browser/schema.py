from opengever.task import _ as task_mf
from plone.directives import form
from zope import schema


class ISimpleResponseForm(form.Schema):
    """Special addresponse form for the forwarding close transition.
    Looks the same, but do something different.
    """

    text = schema.Text(
        title=task_mf('label_response', default="Response"),
        description=task_mf('help_response', default=""),
        required=False,
        )
