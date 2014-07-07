from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base import _
from opengever.base.behaviors.classification import IClassification
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zExceptions import Unauthorized


def can_access_public_trial_edit_form(user, content):
    """Returns True if the user has 'Modify portal content' permission in any
    open dossier state.
    """
    wftool = getToolByName(content, 'portal_workflow')

    assert IBaseDocument.providedBy(
        content), 'Content needs to provide IBaseDocument'

    dossier = aq_parent(aq_inner(content))
    while not IDossierMarker.providedBy(dossier):
        dossier = aq_parent(aq_inner(dossier))
        if IPloneSiteRoot.providedBy(dossier):
            break

    assert IDossierMarker.providedBy(
        dossier), 'The parent needs to be a dossier'

    workflow_id = wftool.getChainForPortalType(dossier.portal_type)[0]
    user_roles = user.getRolesInContext(dossier)

    has_role = False

    for open_state in DOSSIER_STATES_OPEN:
        state = wftool.get(workflow_id).states.get(open_state)

        roles_with_modify = state.permission_roles['Modify portal content']

        has_role = bool(set(roles_with_modify) & set(user_roles))

        if has_role:
            break
        else:
            continue
    return has_role


class EditPublicTrialForm(Form):

    label = _(u'label_change_public_trial',
              default=u'Change public trial information.')
    fields = Fields(IClassification).select('public_trial')

    def update(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        if not can_access_public_trial_edit_form(user, self.context):
            raise Unauthorized('You cannot access this resource.')

        super(EditPublicTrialForm, self).update()

    @buttonAndHandler(_(u'button_save', default=u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()

        if errors:
            return

        self.context.public_trial = data['public_trial']
        self.context.reindexObject(idxs=['public_trial'])

        return self.redirect()

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())
