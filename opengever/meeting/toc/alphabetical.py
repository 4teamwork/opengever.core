from itertools import groupby
from opengever.meeting.model import AgendaItem
from operator import itemgetter
from sqlalchemy.orm import joinedload


def _first_title_char(value):
    return value['title'][:1].upper()


class AlphabeticalToc(object):

    def __init__(self, period):
        self.period = period

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

        # input items must be sorted since grouping depends on input order
        # currently sort on the client side since title can be either in the
        # agenda_items table or in the proposals table.
        sorted_items = sorted(unordered_items,
                              key=itemgetter('title', 'decision_number'))

        results = []
        for character, contents in groupby(sorted_items,
                                           key=_first_title_char):
            results.append({
                'group_title': character,
                'contents': list(contents)
            })
        return sorted(results, key=itemgetter('group_title'))
