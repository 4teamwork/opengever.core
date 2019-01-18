from opengever.meeting import _
from opengever.meeting.toc.dossier_refnum import to_human_sortable_key
from opengever.meeting.toc.dossier_refnum import DossierReferenceNumberBasedTOC
from opengever.meeting.toc.utils import normalise_string
from opengever.meeting.toc.utils import repo_refnum
from zope.globalrequest import getRequest
from zope.i18n import translate


class RepositoryReferenceNumberBasedTOC(DossierReferenceNumberBasedTOC):

    @staticmethod
    def item_sort_key(item):
        return (to_human_sortable_key(repo_refnum(item)),
                normalise_string(item['title']),
                item['title'],
                item['decision_number'])

    @staticmethod
    def group_by_key(item):
        return (to_human_sortable_key(repo_refnum(item)))

    def get_group_title(self, group_key, contents):
        if group_key:
            return repo_refnum(contents[0])

        ad_hoc_title = translate(_(u'ad_hoc_toc_group_title',
                                   default=u'Ad hoc agendaitems'),
                                 context=getRequest())
        return ad_hoc_title
