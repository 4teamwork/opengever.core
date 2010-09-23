from five import grok
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations


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
                      dict(id = 'journal', content=self.journal()),
                      dict(id = 'sharing', content=self.sharing())],
                     [dict(id = 'documents', content=self.documents()), ]]
        else:
            items = [[dict(id = 'subdossiers', content=self.subdossiers()),
                      dict(id = 'tasks', content=self.tasks()),
                      dict(id = 'journal', content=self.journal()),
                      dict(id = 'sharing', content=self.sharing())],
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
            'alt': self.context.toLocalizedTime(
                    document.modified, long_format=1),
            'getIcon': 'document_icon.gif',
        } for document in documents]
        return self.catalog(
            ['opengever.document.document', 'ftw.mail.mail'])[:10]

    def events(self):
        return self.catalog(['dummy.event', ])[:5]

    def journal(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            entries = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])[:5]
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented

        edict = [dict(Title=entry['action']['title'], getIcon=None)
            for entry in reversed(entries)]
        return edict

    def sharing(self):
        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        dossier_adpt = IDossier(self.context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append({'contact': dossier_adpt.responsible,
                        'roles': responsible_name,
                        'role_list': responsible_name,
                        })

        info = getUtility(IContactInformation)

        return [{
            'Title': info.describe(xx['contact']),
            'getURL': info.get_profile_url(xx['contact']),
            'getIcon':'user.gif',
            }
            for xx in results]
