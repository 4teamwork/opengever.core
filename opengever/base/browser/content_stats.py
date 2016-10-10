from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from plone import api
from Products.Five import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate


TYPES = (
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    '_opengever.ereignis',
)


class ContentStatsView(BrowserView):
    """View that displays some basic content statistics (recursively, based
    on current context).
    """

    def get_content_stats(self):
        all_stats = []

        for portal_type in TYPES:
            if portal_type == '_opengever.ereignis':
                type_stats = self.get_manual_journal_entries()
            else:
                type_stats = self.get_stats_for_type(portal_type)

            all_stats.append(type_stats)
        return all_stats

    def get_stats_for_type(self, portal_type):
        catalog = api.portal.get_tool('portal_catalog')
        types_tool = api.portal.get_tool('portal_types')
        fti = types_tool[portal_type]
        title = translate(
            fti.title,
            context=self.request,
            domain=fti.i18n_domain)
        brains = catalog.unrestrictedSearchResults(
            portal_type=portal_type, path=self.get_path())

        open_count = None
        closed_count = None

        # For dossiers, also count open / closed separately
        if portal_type == 'opengever.dossier.businesscasedossier':
            open_brains = catalog.unrestrictedSearchResults(
                portal_type=portal_type, path=self.get_path(),
                review_state='dossier-state-active')
            open_count = len(open_brains)
            closed_brains = catalog.unrestrictedSearchResults(
                portal_type=portal_type, path=self.get_path(),
                review_state='dossier-state-resolved')
            closed_count = len(closed_brains)

        type_stats = {
            'title': title,
            'portal_type': portal_type,
            'total': len(brains),
            'open': open_count,
            'closed': closed_count,
            'search_url': '%s/@@search?portal_type=%s' % (
                self.context.absolute_url(), portal_type),
        }
        return type_stats

    def get_manual_journal_entries(self):
        catalog = api.portal.get_tool('portal_catalog')
        dossier_brains = catalog.unrestrictedSearchResults(
            portal_type='opengever.dossier.businesscasedossier',
            path=self.get_path())

        count = 0
        for brain in dossier_brains:
            dossier = brain.getObject()
            if IAnnotationsJournalizable.providedBy(dossier):
                annotations = IAnnotations(dossier)
                journal = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
                for entry in journal:
                    if entry['action']['type'] == 'manually-journal-entry':
                        count += 1

        type_stats = {
            'title': 'Ereignis',
            'portal_type': '_opengever.ereignis',
            'total': count,
            'open': None,
            'closed': None,
            'search_url': None,
        }
        return type_stats

    def get_path(self):
        return '/'.join(self.context.getPhysicalPath())
