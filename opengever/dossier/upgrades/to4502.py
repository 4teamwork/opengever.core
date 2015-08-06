from ftw.upgrade import UpgradeStep
from plone import api
from zope.annotation.interfaces import IAnnotations


DOSSIER_KEY = 'dossier_reference_mapping'
CHILD_REF_KEY = 'reference_numbers'
PREFIX_REF_KEY = 'reference_prefix'


class DropTemplateDossierReferenceNumber(UpgradeStep):
    """Drop the no longer needed referencenumbers for template dossiers from
    the plone site.

    They are stored in the site's annotations under the key
    'dossier_reference_mapping'.

    Also cleanup potential leftovers from a previous reference number
    migration. Previously refernce numbers were not stored type-specific but
    directly as annotation keys with the keys 'reference_numbers' and
    'reference_prefix'.

    """
    def __call__(self):
        drop_old_refnumber_from_annotations()


def drop_old_refnumber_from_annotations():
    annotations = IAnnotations(api.portal.get())
    for key in [DOSSIER_KEY, CHILD_REF_KEY, PREFIX_REF_KEY]:
        if key in annotations:
            del annotations[key]
