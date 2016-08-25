from opengever.contact.models import Participation
from opengever.tabbedview import GeverTabMixin
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class ParticpationTab(BrowserView, GeverTabMixin):

    show_searchform = False

    template = ViewPageTemplateFile('templates/participations.pt')

    def __call__(self):
        return self.template()

    def get_participations(self):
        """Returns all participations for the current context.
        """
        return Participation.query.by_dossier(self.context).all()
