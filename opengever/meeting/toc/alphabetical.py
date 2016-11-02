from opengever.meeting.model import AgendaItem
from sqlalchemy.orm import joinedload
from operator import itemgetter


class AlphabeticalToc(object):

    def __init__(self, period):
        self.period = period

    def get_json(self):
        agenda_items = AgendaItem.query.options(
            joinedload('proposal'), joinedload('meeting'))

        results = []
        for agenda_item in agenda_items:
            meeting = agenda_item.meeting
            results.append({
                'title': agenda_item.get_title(),
                'dossier_reference_number': agenda_item.get_dossier_reference_number(),
                'repository_folder_title': agenda_item.get_repository_folder_title(),
                'decision_number': agenda_item.decision_number,
                'has_proposal': agenda_item.has_proposal,
                'meeting_date': meeting.get_date(),
                'meeting_start_page_number': meeting.protocol_start_page_number,
            })
        # currently sort on the client side since title can be either in the
        # agenda_items table or in the proposals table.
        return sorted(results, key=itemgetter('title', 'decision_number'))
