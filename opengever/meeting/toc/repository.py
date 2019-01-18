from opengever.meeting import _
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.utils import normalise_string
from zope.globalrequest import getRequest
from zope.i18n import translate


class RepositoryBasedTOC(AlphabeticalToc):

    @staticmethod
    def group_by_key(item):
        return item['repository_folder_title']

    @staticmethod
    def item_sort_key(item):
        return (normalise_string(item['repository_folder_title']),
                item['repository_folder_title'],
                normalise_string(item['title']),
                item['title'],
                item['decision_number'])

    @staticmethod
    def get_group_title(group_key, contents):
        if group_key:
            return group_key

        ad_hoc_title = translate(_(u'ad_hoc_toc_group_title',
                                   default=u'Ad hoc agendaitems'),
                                 context=getRequest())
        return ad_hoc_title
