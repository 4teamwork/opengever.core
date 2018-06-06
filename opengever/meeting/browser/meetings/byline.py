from opengever.base.browser.helper import get_css_class
from opengever.base.utils import escape_html
from opengever.base.viewlets.byline import BylineBase
from opengever.meeting import _
from opengever.tabbedview.helper import linked
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate


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
        if api.user.has_permission('View', obj=dossier):
            dossier_html = linked(dossier, dossier.Title())
        else:
            no_access_tooltip = safe_unicode(translate(
                _(u'You are not allowed to view the meeting dossier.'),
                context=self.request))
            dossier_html = (
                u'<span class="{classes}">'
                u'<span class="no_access" title="{no_access_tooltip}">'
                u'{title}</span></span>').format(
                    classes=safe_unicode(get_css_class(dossier)),
                    no_access_tooltip=escape_html(no_access_tooltip),
                    title=escape_html(safe_unicode(dossier.Title())))

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
