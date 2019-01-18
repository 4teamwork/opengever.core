from opengever.meeting import _
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.utils import to_human_sortable_key
from opengever.meeting.toc.utils import normalise_string
from zope.globalrequest import getRequest
from zope.i18n import translate


class DossierReferenceNumberBasedTOC(AlphabeticalToc):

    @staticmethod
    def group_by_key(item):
        return (to_human_sortable_key(item['dossier_reference_number']))

    @staticmethod
    def item_sort_key(item):
        return (to_human_sortable_key(item['dossier_reference_number']),
                normalise_string(item['title']),
                item['title'],
                item['decision_number'])

    def get_group_title(self, group_key, contents):
        if group_key:
            return contents[0]['dossier_reference_number']

        ad_hoc_title = translate(_(u'ad_hoc_toc_group_title',
                                   default=u'Ad hoc agendaitems'),
                                 context=getRequest())
        return ad_hoc_title
