
from opengever.meeting.toc.alphabetical import AlphabeticalToc


class DecisionSequenceNumberBasedTOC(AlphabeticalToc):
    def sort_items(self, items):
        return sorted(items, key=lambda item: item.get('decision_number') or ' ')

    def get_group_title(self, group_key, contents):
        return ''
