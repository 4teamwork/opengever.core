from markdown import Markdown
from opengever.core.upgrade import SchemaMigration
from plone import api
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


agenda_items_table = table(
    'agendaitems',
    column('id'),
    column('discussion'),
    column('decision'),
)

AGENDA_ITEM_ATTRIBUTES = ['discussion', 'decision']

proposals_table = table(
    'proposals',
    column('id'),
    column('legal_basis'),
    column('initial_position'),
    column('proposed_action'),
    column('considerations'),
    column('publish_in'),
    column('disclose_to'),
    column('copy_for_attention'),
)

PROPOSAL_ATTRIBUTES = ['legal_basis',
                       'initial_position',
                       'proposed_action',
                       'considerations',
                       'publish_in',
                       'disclose_to',
                       'copy_for_attention']


class ConvertMarkdownToHTML(SchemaMigration):
    """Convert all Markdown fields to HTML.

    We switched to trix which stores/requires HTML. This migration is
    semi-automatic only, it requires a client-side round-trip over trix to
    have the same markup as supplied by trix.

    """
    profileid = 'opengever.meeting'
    upgradeid = 4630

    def migrate(self):
        self.initialize()
        self.convert_markdown_to_html()

    def initialize(self):
        self.transformer = api.portal.get_tool('portal_transforms')
        # in Markdown 2.0.3 only html4 is available
        self.markdown = Markdown(safe_mode=False, output_format='html4')

    def convert_markdown_to_html(self):
        for agenda_item in self.execute(agenda_items_table.select()):
            self._convert_agenda_item(agenda_item)

        for proposal in self.execute(proposals_table.select()):
            self._convert_proposal(proposal)

    def _convert_agenda_item(self, agenda_item):
        agenda_item_attributes = self._get_converted_attributes(
            agenda_item, AGENDA_ITEM_ATTRIBUTES)
        self.execute(agenda_items_table
                     .update()
                     .where(agenda_items_table.c.id == agenda_item.id)
                     .values(**agenda_item_attributes))

    def _convert_proposal(self, proposal):
        if not proposal:
            return

        proposal_attributes = self._get_converted_attributes(
            proposal, PROPOSAL_ATTRIBUTES)
        self.execute(proposals_table
                     .update()
                     .where(proposals_table.c.id == proposal.id)
                     .values(**proposal_attributes))

    def _get_converted_attributes(self, obj, attributes):
        """Convert all attributes of obj to html and return a dict with the
        converted values.

        """
        converted_attributes = {}
        for attribute_name in attributes:
            value = getattr(obj, attribute_name)
            converted_attributes[attribute_name] = self._convert_to_html(value)
        return converted_attributes

    def _convert_to_html(self, value):
        """Convert a markdown value to HTML.

        In case value is HTML already (i.e. was already converted or stored
        with trix) it won't be changed by the conversion since we don't run
        it in safe_mode.

        Also converts the value to `safe_html` with a plone transform. This is
        not necessary at all but i'd like to have the same pipeline applied
        as in the corresponding widget and on the protocol page.

        """
        return self._html_to_safe_html(self._md_to_html(value))

    def _md_to_html(self, value):
        # keep empty data (whatever it is), it makes markdown unhappy
        if not value:
            return value

        self.markdown.reset()
        return self.markdown.convert(value)

    def _html_to_safe_html(self, value):
        # keep empty data (whatever it is), it makes transform unhappy
        if not value:
            return value
        return self.transformer.convert('safe_html', value).getData()
