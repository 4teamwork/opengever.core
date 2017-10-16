from opengever.dossier.browser.overview import DossierOverview
from opengever.meeting import _


class MeetingDossierOverview(DossierOverview):

    def boxes(self):
        """Insert meeting box first in overview's **middle** column."""

        boxes = super(MeetingDossierOverview, self).boxes()

        column = boxes[0]
        column.insert(0, self.build_linked_meeting_box())
        return boxes

    def build_linked_meeting_box(self):
        box = {'id': 'linked_meeting',
               'content': self.linked_meeting(),
               'label': _('label_linked_meeting', default='Linked meeting')}
        return box

    def linked_meeting(self):
        content = []
        meeting = self.context.get_meeting()
        if meeting:
            content.append({
                'Title': meeting.get_title(),
                'getURL': meeting.get_url(),
                'css_class': meeting.css_class,
            })
        return content
