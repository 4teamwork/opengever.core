from ftw.tabbedview.interfaces import ITabbedView
from opengever.base.response import JSONResponse
from opengever.contact import _
from opengever.contact.models import ContactParticipation
from opengever.contact.models import Participation
from opengever.tabbedview import GeverTabMixin
from plone import api
from Products.Five.browser import BrowserView
from sqlalchemy import desc
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


class ParticipationsView(BrowserView):
    """An endpoint to fetch all participations for the current contact.
    """

    def get_slice_size(self):
        return api.portal.get_registry_record(
            'batch_size', interface=ITabbedView)

    def list(self):
        """Returns a json dict with the following structure.

        `participations`: a list of json representation of the current
        contexts participations. It sliced to the default tabbedview batch
        size depending on the `show_all` request_flag.
        `has_more`: a boolean value if the list is sliced.
        `show_all_label`: label for the show all link.
        """

        data = {}
        # XXX also include OrgRoleParticipations for that person
        query = ContactParticipation.query.by_participant(self.context.model)
        query = query.order_by(desc(Participation.participation_id))
        total = query.count()

        if self.request.get('show_all') != 'true':
            query = query.limit(self.get_slice_size())

        data['participations'] = self._serialize(query)
        data['has_more'] = total > len(data['participations'])
        data['show_all_label'] = self.get_show_all_label(total)
        return JSONResponse(self.request).data(**data).dump()

    def get_show_all_label(self, total):
        msg = _(u'label_show_all',
                default=u'Show all ${total} participations',
                mapping={'total': total})
        return translate(msg, context=self.request)

    def _serialize(self, participations):
        return [participation.get_json_representation()
                for participation in participations]


class ParticpationTab(BrowserView, GeverTabMixin):

    show_searchform = False

    template = ViewPageTemplateFile('templates/participations.pt')

    def __call__(self):
        return self.template()

    def get_participations(self):
        """Returns all participations for the current context.
        """
        return Participation.query.by_dossier(self.context).all()
