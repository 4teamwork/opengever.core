from opengever.meeting.toc.alphabetical import AlphabeticalToc


class DecisionSequenceNumberBasedTOC(AlphabeticalToc):
    def sort_items(self, items):
        return sorted(items, key=lambda item: item.get('decision_number') or ' ')

    def group_items(self, sorted_items):
        return [{'group_title': '', 'contents': sorted_items}]
