from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.task import _
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.supermodel.model import Schema
from zope import schema
from zope.component import adapter
from zope.interface import implementer


class IResponse(Schema):

    text = schema.Text(
        title=_('label_response', default="Response"),
        required=False,
        )


class INewDeadline(Schema):

    new_deadline = schema.Date(
        title=_(u"label_new_deadline", default=u"New Deadline"),
        required=True)


@implementer(ITransitionExtender)
@adapter(ITask)
class AcceptTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class ModifyDeadlineTransitionExtender(TransitionExtender):

    schemas = [INewDeadline, ]

    def after_transition_hook(self, transition, **kwargs):
        IDeadlineModifier(self.context).modify_deadline(
            kwargs['new_deadline'], kwargs.get('text'), transition)


@implementer(ITransitionExtender)
@adapter(ITask)
class ResolveTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class CloseTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))
