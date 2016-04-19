from five import grok
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDisposition
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class Appraisal(grok.Adapter):
    """Basic reference number adapter.
    """
    grok.provides(IAppraisal)
    grok.context(IDisposition)

    key = 'disposition_appraisal'

    def __init__(self, context):
        super(Appraisal, self).__init__(context)
        self._annotations = IAnnotations(self.context)
        if self.key not in self._annotations.keys():
            self._annotations[self.key] = PersistentDict()

    @property
    def storage(self):
        return self._annotations[self.key]

    def initialize(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        self.storage[intid] = self.get_pre_appraisal(dossier)

    def get_pre_appraisal(self, dossier):
        """Checks the preselection in the archive_value field and return
        if the dossier should be archived or not.
        """
        return ILifeCycle(dossier).archival_value != ARCHIVAL_VALUE_UNWORTHY

    def get(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        return self.storage.get(intid)

    def update(self, dossier=None, intid=None, archive=True):
        if not intid and not dossier:
            raise ValueError('dossier or intid needed.')

        if not intid:
            intid = getUtility(IIntIds).getId(dossier)

        self.storage[intid] = archive

    def drop(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        self.storage.pop(intid)
