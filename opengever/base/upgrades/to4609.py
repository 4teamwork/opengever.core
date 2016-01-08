from ftw.upgrade import UpgradeStep
from Products.Transience.Transience import Increaser
from zope.annotation.interfaces import IAnnotations


SEQUENCE_NUMBER_ANNOTATION_KEY = 'ISequenceNumber.sequence_number'


class MigrateSequenceNumberIncreasers(UpgradeStep):

    def __call__(self):
        annotations = IAnnotations(self.portal)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in annotations:
            return

        mapping = annotations[SEQUENCE_NUMBER_ANNOTATION_KEY]
        for key in mapping:
            if isinstance(mapping[key], Increaser):
                mapping[key] = mapping[key]()
