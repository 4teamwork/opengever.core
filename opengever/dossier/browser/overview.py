from five import grok
from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.base.browser.helper import get_css_class
from opengever.dossier import _
from opengever.dossier import _ as _dossier
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview.browser.base import OpengeverTab
from sqlalchemy import desc


class DossierOverview(BoxesViewMixin, grok.View, OpengeverTab):

    show_searchform = False

    grok.context(IDossierMarker)
    grok.name('tabbedview_view-overview')
    grok.require('zope2.View')
    grok.template('overview')

    def catalog(self, types, showTrashed=False, depth=2):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(depth=depth,
                      query='/'.join(self.context.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

    def boxes(self):
        return [
            [
                dict(id='newest_tasks', content=self.tasks(),
                     href='tasks', label=_("Newest tasks")),
                dict(id='participants', content=self.sharing(),
                     href='participants', label=_("Participants")),
            ], [
                dict(id='newest_documents', content=self.documents(),
                     href='documents', label=_("Newest documents")),
                dict(id='description', content=self.description,
                     label=_("Description")),
            ]
        ]

    def subdossiers(self):
        return self.context.get_subdossiers(
            sort_on='modified', sort_order='reverse',
            review_state=DOSSIER_STATES_OPEN)[:5]

    def tasks(self):
        return Task.query.by_container(self.context, get_current_admin_unit())\
                         .order_by(desc('modified')).limit(5).all()

    def documents(self):
        documents = self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ])[:10]
        document_list = [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': document.document_date and
            document.document_date.strftime('%d.%m.%Y') or '',
            'css_class': get_css_class(document),
            'portal_type': document.portal_type,
            } for document in documents]

        return document_list

    def sharing(self):
        # get the participants
        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        # also append the responsible
        class ResponsibleParticipant(object):
            pass

        responsible = ResponsibleParticipant()
        responsible.roles = _dossier(u'label_responsible', 'Responsible')
        responsible.role_list = responsible.roles

        dossier_adpt = IDossier(self.context)
        responsible.contact = dossier_adpt.responsible
        results.append(responsible)

        users = []
        for dossier in results:
            actor = Actor.lookup(dossier.contact)
            users.append({
                'Title': actor.get_label(),
                'getURL': actor.get_profile_url(),
                'css_class': 'function-user',
            })
        return users

    def description(self):
        return self.context.description
