from Products.CMFCore.utils import getToolByName
from plone.app.testing import applyProfile
from plone.browserlayer.utils import unregister_layer
from plone.dexterity.schema import SCHEMA_CACHE
import transaction


def activate_filing_number(portal):
    applyProfile(portal, 'opengever.dossier:filing')
    transaction.commit()


def inactivate_filing_number(portal):
    unregister_layer('opengever.dossier.filing')

    portal_types = getToolByName(portal, 'portal_types')
    fti = portal_types.get('opengever.dossier.businesscasedossier')
    fti.behaviors = [behavior for behavior in fti.behaviors
                     if not behavior.endswith('IFilingNumber')]

    SCHEMA_CACHE.invalidate('opengever.dossier.businesscasedossier')
