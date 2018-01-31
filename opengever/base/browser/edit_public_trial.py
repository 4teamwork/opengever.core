from opengever.base import _
from opengever.base.behaviors.classification import IClassification
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.dossier.utils import find_parent_dossier
from plone.dexterity.browser.edit import DefaultEditForm
from Products.CMFCore.utils import getToolByName
from z3c.form.field import Fields
from zExceptions import Unauthorized


def can_access_public_trial_edit_form(user, content):
    """Returns True if the user has 'Modify portal content' permission in any
    open dossier state. And the containing dossier is
     - not a templatefolder
     - not inactive
    """

    assert IBaseDocument.providedBy(
        content), 'Content needs to provide IBaseDocument'

    wftool = getToolByName(content, 'portal_workflow')
    dossier = find_parent_dossier(content)

    if ITemplateFolder.providedBy(dossier):
        return False

    if wftool.getInfoFor(dossier, 'review_state') == 'dossier-state-inactive':
        return False

    workflow_id = wftool.getChainForPortalType(dossier.portal_type)[0]
    user_roles = user.getRolesInContext(dossier)

    has_role = False

    for open_state in DOSSIER_STATES_OPEN:
        state = wftool.get(workflow_id).states.get(open_state)

        if state is None:
            continue

        roles_with_modify = state.permission_roles['Modify portal content']

        has_role = bool(set(roles_with_modify) & set(user_roles))

        if has_role:
            break
        else:
            continue
    return has_role


class EditPublicTrialForm(DefaultEditForm):

    schema = None

    fields = Fields(IClassification).select(
        'public_trial', 'public_trial_statement')

    label = _(u'label_change_public_trial',
              default=u'Change public trial information.')

    def update(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        if not can_access_public_trial_edit_form(user, self.context):
            raise Unauthorized('You cannot access this resource.')

        super(EditPublicTrialForm, self).update()
