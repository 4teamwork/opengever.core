from opengever.document import _
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.dossier.utils import find_parent_dossier
from plone import api
from plone.dexterity.browser.edit import DefaultEditForm
from z3c.form.field import Fields
from zExceptions import Unauthorized


def can_access_archival_file_form(user, content):
    """Returns True if the user has 'Modify portal content' permission in any
    open dossier state. And the containing dossier is
     - not a templatefolder
     - not inactive
    """

    assert IBaseDocument.providedBy(
        content), 'Content needs to provide IBaseDocument'

    dossier = find_parent_dossier(content)
    if ITemplateFolder.providedBy(dossier):
        return False
    if api.content.get_state(obj=dossier) == 'dossier-state-inactive':
        return False

    wftool = api.portal.get_tool('portal_workflow')
    workflow_id = wftool.getChainForPortalType(dossier.portal_type)[0]
    user_roles = user.getRolesInContext(dossier)

    for open_state in DOSSIER_STATES_OPEN:
        state = wftool.get(workflow_id).states.get(open_state)
        roles_with_modify = state.permission_roles['Modify portal content']
        return bool(set(roles_with_modify).intersection(user_roles))

    return False


class EditArchivalFileForm(DefaultEditForm):
    schema = None
    fields = Fields(IDocumentMetadata).select('archival_file')
    label = _(u'label_change_archival_file', default=u'Change archival file')

    def update(self):
        user = api.user.get_current()
        if not can_access_archival_file_form(user, self.context):
            raise Unauthorized('You cannot access this resource.')

        super(EditArchivalFileForm, self).update()
