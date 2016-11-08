from itertools import groupby
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from operator import itemgetter


class RepositoryBasedTOC(AlphabeticalToc):

    def sort_items(self, unordered_items):
        return sorted(unordered_items,
                      key=itemgetter('repository_folder_title',
                                     'title',
                                     'decision_number'))

    def group_items(self, sorted_items):
        results = []
        for repo_folder_title, contents in groupby(
                    sorted_items, key=itemgetter('repository_folder_title')):
            results.append({
                'group_title': repo_folder_title,
                'contents': list(contents)
            })
        return results
