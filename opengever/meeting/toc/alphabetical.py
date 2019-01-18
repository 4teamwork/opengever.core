from datetime import datetime
from datetime import time
from datetime import timedelta
from itertools import groupby
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.meeting.toc.utils import first_title_char
from opengever.meeting.utils import format_date
from opengever.meeting.utils import JsonDataProcessor
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import false
import pytz


class AlphabeticalToc(object):

    def __init__(self, period):
        self.period = period

    @staticmethod
    def group_by_key(item):
        return first_title_char(item)

    @staticmethod
    def item_sort_key(item):
        return (item['title'].lower(),
                item['repository_folder_title'],
                item['decision_number'])

    def sort_items(self, unordered_items):
        """We currently sort on the client side since title can be either in
        the agenda_items table or in the proposals table.
        """
        return sorted(unordered_items, key=self.item_sort_key)

    def group_items(self, sorted_items):
        """Input items must be sorted since groupby depends on input order.
        """
        results = []
        for character, contents in groupby(sorted_items,
                                           key=self.group_by_key):
            results.append({
                'group_title': character,
                'contents': list(contents)
            })
        return results

    def sort_groups(self, groups):
        return groups

    def build_query(self):
        datetime_from = pytz.UTC.localize(
            datetime.combine(self.period.date_from, time(0, 0)))
        datetime_to = pytz.UTC.localize(
            datetime.combine(self.period.date_to + timedelta(days=1),
                             time(0, 0)))

        # we need the explicit join to filter below and to avoid a cross-join
        # without on-condition.
        query = AgendaItem.query.join(Meeting).options(
            joinedload('proposal'), contains_eager('meeting'))
        # we only have a look at the start-date of a meeting to decide the
        # relevant day for the toc
        query = query.filter(Meeting.start >= datetime_from,
                             Meeting.start < datetime_to,
                             Meeting.committee == self.period.committee,
                             AgendaItem.is_paragraph == false()
                             )
        return query

    def get_json(self):
        processor = JsonDataProcessor()
        data_fields = (("meeting_date", ),)
        transforms = (format_date,)
        unordered_items = []
        for agenda_item in self.build_query():
            meeting = agenda_item.meeting
            unordered_items.append(processor.process(
                {
                 'title': agenda_item.get_title(),
                 'dossier_reference_number': agenda_item.get_dossier_reference_number(),
                 'repository_folder_title': agenda_item.get_repository_folder_title(),
                 'decision_number': agenda_item.decision_number,
                 'has_proposal': agenda_item.has_proposal,
                 'meeting_date': meeting.start,
                 'meeting_start_page_number': meeting.protocol_start_page_number,
                }, data_fields, transforms))
        sorted_items = self.sort_items(unordered_items)
        grouped_results = self.group_items(sorted_items)
        return {'toc': self.sort_groups(grouped_results)}
