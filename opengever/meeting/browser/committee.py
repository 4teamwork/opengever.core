from opengever.meeting import _
from opengever.meeting.period import Period
from opengever.tabbedview import GeverTabMixin
from Products.Five.browser import BrowserView


class CommitteeOverview(BrowserView, GeverTabMixin):
    """The overview tab for the committee tabbeview.
    """

    show_searchform = False

    def boxes(self):
        items = [
            [{'id': 'upcoming_meetings',
              'label': _('label_upcoming_meetings', default=u'Upcoming meetings'),
              'content': self.upcoming_meetings(),
              'href': 'meetings'},
             {'id': 'closed_meetings',
              'label': _('label_closed_meetings', default=u'Closed meetings'),
              'content': self.closed_meetings(),
              'href': 'meetings'}],

            [{'id': 'unscheduled_proposals',
              'label': _('label_unscheduled_proposals',
                         default=u'Unscheduled proposals'),
              'content': self.unscheduled_proposals(),
              'href': 'submittedproposals'}],

            [{'id': 'period',
              'label': _('label_current_period', default=u'Current Period'),
              'content': [self.period()],
              'href': ''},
             {'id': 'current_members',
              'label': _('label_current_members',
                         default=u'Current members'),
              'content': self.current_members(),
              'href': 'memberships'}],
        ]

        return items

    def upcoming_meetings(self):
        meetings = self.context.get_upcoming_meetings()
        return [meeting.get_link() for meeting in meetings[:10]]

    def closed_meetings(self):
        meetings = self.context.get_closed_meetings()
        return [meeting.get_link() for meeting in meetings[:10]]

    def unscheduled_proposals(self):
        proposals = self.context.get_unscheduled_proposals()
        return [proposal.get_submitted_link() for proposal in proposals]

    def current_members(self):
        members = self.context.get_active_members().all()
        committee_container = self.context.get_committee_container()
        return [member.get_link(committee_container) for member in members]

    def period(self):
        period = Period.get_current(self.context)
        if period is None:
            return _(u'No content')
        return period.extended_title
