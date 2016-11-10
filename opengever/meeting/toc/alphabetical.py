from itertools import groupby
from opengever.meeting.model import AgendaItem
from operator import itemgetter
from sqlalchemy.orm import joinedload


def first_title_char(value):
    return value['title'][:1].upper()


def item_sort_key(item):
    return (first_title_char(item), item['decision_number'])


class AlphabeticalToc(object):

    def __init__(self, period):
        self.period = period

    def sort_items(self, unordered_items):
        """We currently sort on the client side since title can be either in
        the agenda_items table or in the proposals table.
        """
        return sorted(unordered_items, key=item_sort_key)

    def group_items(self, sorted_items):
        """Input items must be sorted since groupby depends on input order.
        """
        results = []
        for character, contents in groupby(sorted_items,
                                           key=first_title_char):
            results.append({
                'group_title': character,
                'contents': list(contents)
            })
        return results

    def sort_groups(self, groups):
        return sorted(groups, key=itemgetter('group_title'))

    def get_json(self):
        agenda_items = AgendaItem.query.options(
            joinedload('proposal'), joinedload('meeting'))

        unordered_items = []
        for agenda_item in agenda_items:
            meeting = agenda_item.meeting
            unordered_items.append({
                'title': agenda_item.get_title(),
                'dossier_reference_number': agenda_item.get_dossier_reference_number(),
                'repository_folder_title': agenda_item.get_repository_folder_title(),
                'decision_number': agenda_item.decision_number,
                'has_proposal': agenda_item.has_proposal,
                'meeting_date': meeting.get_date(),
                'meeting_start_page_number': meeting.protocol_start_page_number,
            })

        sorted_items = self.sort_items(unordered_items)
        grouped_results = self.group_items(sorted_items)
        return {'toc': self.sort_groups(grouped_results)}
