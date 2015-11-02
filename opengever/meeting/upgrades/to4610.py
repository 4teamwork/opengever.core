from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer


class AddProtocolStartPage(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4610

    def migrate(self):
        self.add_protocol_start_page_number_column()

    def add_protocol_start_page_number_column(self):
        self.op.add_column(
            'meetings', Column('protocol_start_page_number', Integer))
