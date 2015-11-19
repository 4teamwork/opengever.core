from five import grok
from opengever.meeting import _
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Period
from opengever.tabbedview.browser.base import OpengeverTab


class CommitteeOverview(grok.View, OpengeverTab):
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
