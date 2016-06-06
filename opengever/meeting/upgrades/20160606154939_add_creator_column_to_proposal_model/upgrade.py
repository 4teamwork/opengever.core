from opengever.core.upgrade import SchemaMigration
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


# copied from from opengever.ogds.models.USER_ID_LENGTH
USER_ID_LENGTH = 255


class AddCreatorColumnToProposalModel(SchemaMigration):
    """Add creator column to proposal model.
    """

    def migrate(self):
        self.add_creator_column()
        self.migrate_creator_from_plone_proxy()
        self.make_creator_column_not_nullable()

    def add_creator_column(self):
        self.op.add_column('proposals',
                           Column('creator',
                                  String(USER_ID_LENGTH),
                                  nullable=True))

    def migrate_creator_from_plone_proxy(self):
        proposals_table = table(
            'proposals',
            column('proposal_id'),
            column('admin_unit_id'),
            column('int_id'),
            column('creator')
        )

        catalog = api.portal.get_tool('portal_catalog')
        proposals = catalog(portal_type='opengever.meeting.proposal')

        intids = getUtility(IIntIds)
        admin_unit_id = get_current_admin_unit().id()

        for proposal in proposals:
            proposal = proposal.getObject()
            self.execute(
                proposals_table.update()
                .values(creator=proposal.Creator())
                .where(proposals_table.c.int_id == intids.getId(proposal))
                .where(proposals_table.c.admin_unit_id == admin_unit_id))

    def make_creator_column_not_nullable(self):
        self.op.alter_column('proposals', 'creator',
                             existing_type=String(USER_ID_LENGTH),
                             nullable=False)
