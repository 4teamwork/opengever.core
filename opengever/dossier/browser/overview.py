from five import grok
from opengever.dossier import _ as _dossier
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from zope.component import getUtility


class DossierOverview(grok.View, OpengeverTab):
    grok.context(IDossierMarker)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def catalog(self, types, showTrashed=False, depth=2):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(depth=depth,
                query='/'.join(self.context.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

    def boxes(self):
        if not self.context.show_subdossier():
            items = [[dict(id = 'tasks', content=self.tasks()),
                      dict(id = 'participants', content=self.sharing())],
                     [dict(id = 'documents', content=self.documents()), ]]
        else:
            items = [[dict(id = 'subdossiers', content=self.subdossiers()),
                      dict(id = 'tasks', content=self.tasks()),
                      dict(id = 'participants', content=self.sharing())],
                     [dict(id = 'documents', content=self.documents()), ]]
        return items

    def subdossiers(self):
        return self.catalog(
            ['opengever.dossier.projectdossier',
                'opengever.dossier.businesscasedossier', ],
            depth=1)[:5]

    def tasks(self):
        return self.catalog(['opengever.task.task', ])[:5]

    def documents(self):
        documents = self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ])[:10]

        return [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': document.document_date.strftime('%d.%m.%Y'),
            'getIcon': document.getIcon,
        } for document in documents]
        return self.catalog(
            ['opengever.document.document', 'ftw.mail.mail'])[:10]

    def events(self):
        return self.catalog(['dummy.event', ])[:5]

    def sharing(self):

        # get the participants
        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        # also append the responsible
        class ResponsibleParticipant(object): pass

        responsible = ResponsibleParticipant()
        responsible.roles = _dossier(u'label_responsible', 'Responsible')
        responsible.role_list = responsible.roles

        dossier_adpt = IDossier(self.context)
        responsible.contact = dossier_adpt.responsible
        results.append(responsible)

        info = getUtility(IContactInformation)

        return [{
            'Title': info.describe(xx.contact),
            'getURL': info.get_profile_url(xx.contact),
            'getIcon':'user.gif',
            }
            for xx in results]
