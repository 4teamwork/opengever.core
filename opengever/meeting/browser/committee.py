from five import grok
from opengever.meeting import _
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Period
from opengever.tabbedview import GeverTabMixin
from plone import api
from Products.Five import BrowserView


class CommitteeOverview(grok.View, GeverTabMixin):
    """The overview tab for the committee tabbeview.
    """
    grok.context(ICommittee)
    grok.name('tabbedview_view-overview')
    grok.require('zope2.View')
    grok.template('overview')

    show_searchform = False

    def boxes(self):
        items = [
            [{'id': 'period',
              'label': _('label_current_period', default=u'Current Period'),
              'content': [self.period()],
              'href': ''},
             {'id': 'upcoming_meetings',
              'label': _('label_upcoming_meetings', default=u'Upcoming meetings'),
              'content': self.upcoming_meetings(),
              'href': 'meetings'}],

            [{'id': 'unscheduled_proposals',
              'label': _('label_unscheduled_proposals',
                         default=u'Unscheduled proposals'),
              'content': self.unscheduled_proposals(),
              'href': 'submittedproposals'}],

            [{'id': 'current_members',
              'label': _('label_current_members',
                         default=u'Current members'),
              'content': self.current_members(),
              'href': 'memberships'}]]

        return items

    def upcoming_meetings(self):
        meetings = self.context.get_upcoming_meetings()
        return [meeting.get_link() for meeting in meetings[:10]]

    def unscheduled_proposals(self):
        proposals = self.context.get_unscheduled_proposals()
        return [proposal.get_submitted_link() for proposal in proposals]

    def current_members(self):
        memberships = self.context.get_active_memberships().all()
        members = [membership.member for membership in memberships]
        return [member.get_link(self.context) for member in members]

    def period(self):
        period = Period.query.get_current(self.context.load_model())
        return period.get_title()


class DeactivateCommittee(BrowserView):

    transition_id = 'active-inactive'

    def __call__(self):
        model = self.context.load_model()

        if model.has_pending_meetings():
            api.portal.show_message(
                message=_('msg_pending_meetings',
                          default=u'Not all meetings are closed.'),
                request=self.request, type='error')

            return self.redirect()

        if model.has_unscheduled_proposals():
            api.portal.show_message(
                message=_('msg_unscheduled_proposals',
                          default=u'There are unscheduled proposals submitted'
                          ' to this committee.'),
                request=self.request, type='error')

            return self.redirect()

        model.deactivate()
        api.portal.show_message(
            message=_(u'label_committe_deactivated',
                      default="Committee deactivated successfully"),
            request=self.request, type='info')

        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def available(self):
        model = self.context.load_model()
        transition = model.workflow.transitions.get(self.transition_id)
        return transition in model.get_state().transitions


class ReactivateCommittee(BrowserView):

    transition_id = 'inactive-active'

    def __call__(self):
        self.context.load_model().reactivate()
        api.portal.show_message(
            message=_(u'label_committe_reactivated',
                      default="Committee reactivated successfully"),
            request=self.request, type='info')

        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def available(self):
        model = self.context.load_model()
        transition = model.workflow.transitions.get(self.transition_id)
        return transition in model.get_state().transitions
