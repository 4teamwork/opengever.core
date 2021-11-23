from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.disposition import IDispositionSchema
from zExceptions import Forbidden
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(ITransitionExtender)
@adapter(IDispositionSchema, IBrowserRequest)
class AppraiseTransitionExtender(TransitionExtender):

    def deserialize(self, transition_params):
        if not IAppraisal(self.context).is_complete():
            raise Forbidden(
                _(u'msg_appraisal_incomplete',
                  default=u'The appraisal is incomplete, appraisal could not'
                  ' be finalized.'))

        return super(AppraiseTransitionExtender, self).deserialize(
            transition_params)
