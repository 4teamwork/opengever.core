from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.utils import normalise_string


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
    def group_key_to_title(group_key):
        return group_key
