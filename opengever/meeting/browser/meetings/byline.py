from opengever.base.viewlets.byline import BylineBase
from opengever.meeting import _
from opengever.tabbedview.helper import linked
from plone import api
from Products.CMFPlone.utils import safe_unicode


class MeetingByline(BylineBase):

    def byline_items(self):
        meeting = self.context.model
        yield {'class': 'byline-meeting-wf-state-{}'.format(meeting.workflow_state),
               'label': _('meeting_byline_workflow_state', default='State'),
               'content': meeting.get_state().title}

        yield {'label': _('meeting_byline_start', default='Start'),
               'content': meeting.get_start()}

        if meeting.get_end():
            yield {'label': _('meeting_byline_end', default='End'),
                   'content': meeting.get_end()}

        yield self.get_role_item(
            'byline-presidency',
            _('meeting_byline_presidency', default='Presidency'),
            meeting.presidency)
        yield self.get_role_item(
            'byline-secretary',
            _('meeting_byline_secretary', default='Secretary'),
            meeting.secretary)

        if meeting.location:
            yield {'label': _('meeting_byline_location', default='Location'),
                   'content': meeting.location}

        dossier = meeting.get_dossier()
        with_tooltip = False
        if api.user.has_permission('View', obj=dossier):
            with_tooltip = True

        dossier_html = linked(dossier, dossier.Title(), with_tooltip=with_tooltip)

        yield {'label': _('meeting_byline_meetin_dossier', default='Meeting dossier'),
               'content': dossier_html,
               'replace': True}

    def get_role_item(self, classname, label, member):
        if member:
            return {'class': classname,
                    'label': label,
                    'content': member.fullname}
        else:
            return {'class': classname + ' hidden',
                    'label': label,
                    'content': ' '}

    def get_items(self):
        items = []

        for item in self.byline_items():
            item['content'] = safe_unicode(item['content'])
            item.setdefault('class', '')
            item.setdefault('replace', False)
            items.append(item)

        return items
