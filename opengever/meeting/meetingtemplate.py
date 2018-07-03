from opengever.meeting.paragraphtemplate import ParagraphTemplate
from plone.dexterity.content import Container
from Products.CMFPlone.utils import safe_unicode


class MeetingTemplate(Container):

    def apply(self, meeting):
        for paragraph in self.get_paragraphs():
            meeting.schedule_text(safe_unicode(paragraph.title),
                                  is_paragraph=True)

    def get_paragraphs(self):
        return [
            paragraph
            for _, paragraph in self.contentItems()
            if isinstance(paragraph, ParagraphTemplate)
        ]
