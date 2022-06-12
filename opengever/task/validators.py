from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.task import _
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.uuid.interfaces import IUUID
from z3c.form import validator
from z3c.relationfield.interfaces import IRelationList
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import Invalid


def get_checked_out_documents(intids):
    checked_out = []
    intid_utility = getUtility(IIntIds)
    request = getRequest()
    for intid in intids:
        doc = intid_utility.getObject(intid)
        manager = getMultiAdapter((doc, request),
                                  ICheckinCheckoutManager)
        if manager.get_checked_out_by():
            checked_out.append(doc)
    return checked_out


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
                    default=u'The documents (${title}) are still checked out. '
                            u'Please check them in first.',
                    mapping={'title': ', '.join(checkedout)}))
