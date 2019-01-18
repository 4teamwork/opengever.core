from opengever.meeting.toc.alphabetical import AlphabeticalToc


class RepositoryBasedTOC(AlphabeticalToc):

    @staticmethod
    def group_by_key(item):
        return item['repository_folder_title']

    @staticmethod
    def item_sort_key(item):
        return (item['repository_folder_title'],
                item['title'],
                item['decision_number'])
