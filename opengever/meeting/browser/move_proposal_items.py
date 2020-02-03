from opengever.base.source import DossierPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.move_items import MoveItemsForm
from opengever.meeting import _
from plone import api
from plone.z3cform import layout
from z3c.form import field
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface


class IMoveProposalItemsSchema(Interface):
    destination_folder = RelationChoice(
        title=_('label_destination', default="Destination"),
        source=DossierPathSourceBinder(
            review_state=DOSSIER_STATES_OPEN,
            object_provides=[
                'opengever.dossier.behaviors.dossier.IDossierMarker',
                ],
            navigation_tree_query={
                'object_provides': [
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                ],
                'review_state': DOSSIER_STATES_OPEN
                },
            ),
        required=True,
        )

    # We Use TextLine here because Tuple and List have no hidden_mode.
    request_paths = schema.TextLine(title=u"request_paths")


class MoveProposalItemsForm(MoveItemsForm):

    fields = field.Fields(IMoveProposalItemsSchema)


class MoveProposalItemsFormView(layout.FormWrapper):
    """ View to move selected proposal items into another location
    """

    form = MoveProposalItemsForm

    def assert_valid_container_state(self):
        container = self.context
        if not container.is_open():
            msg = _(u'error_move_proposal_dossier_not_open',
                    default=u'Can only move objects from open dossiers')
            api.portal.show_message(msg, request=self.request, type='error')
            self.request.RESPONSE.redirect(
                '%s#proposals' % container.absolute_url())

    def render(self):
        self.assert_valid_container_state()
        if not self.request.get('paths') and not \
                self.form_instance.widgets['request_paths'].value:
            msg = _(u'error_no_items_selected',
                    default=u'You have not selected any items')
            api.portal.show_message(msg, request=self.request, type='error')

            return self.request.RESPONSE.redirect(
                '%s#proposals' % self.context.absolute_url())
        return super(MoveProposalItemsFormView, self).render()
