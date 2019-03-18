from opengever.task import _
from opengever.task import is_private_task_feature_enabled
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.uuid.interfaces import IUUID
from z3c.form import validator
from z3c.form.interfaces import IEditForm
from z3c.relationfield.interfaces import IRelationList
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Invalid


class NoCheckedoutDocsValidator(validator.SimpleFieldValidator):
    """Validator wich checks that all selected documents are checked in."""

    def validate(self, value):

        if value:

            intids = getUtility(IIntIds)

            checkedout = []
            for iid in value:
                if not IRelationList.providedBy(self.field):
                    iid = int(iid)
                    doc = intids.getObject(int(iid))
                else:
                    doc = iid

                brain = uuidToCatalogBrain(IUUID(doc))
                if brain.checked_out:
                    checkedout.append(doc.title)

            if len(checkedout):
                raise Invalid(_(
                        u'error_checked_out_document',
                        default=u'The documents (${title}) are still checked out. \
                                Please checkin them in bevore deliver',
                        mapping={'title': ', '.join(checkedout)}))


class PrivateTaskValidator(validator.SimpleFieldValidator):
    """Check the private task feature is enabled."""

    def validate(self, value, force=False):
        # Group < TaskEditForm
        if IEditForm.providedBy(self.view._parent):
            raise Invalid(_(
                u'error_private_tasks_status_not_editable',
                default=u'The private task status may not be edited.',
            ))
        if not is_private_task_feature_enabled():
            raise Invalid(_(
                u'error_private_tasks_not_enabled',
                default=u'The private tasks feature is not enabled.',
            ))
