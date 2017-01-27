from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDisposition
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds


@implementer(IAppraisal)
@adapter(IDisposition)
class Appraisal(object):
    """Adapter for disposition objects, which stores the archival appraisal
    for each dossiers in the annotations of the context (disposition).
    """

    key = 'disposition_appraisal'

    def __init__(self, context):
        self.context = context
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
        it if exists.

        Sampling, unchecked and prompt aren't handled as a preselection.
        """
        archival_value = ILifeCycle(dossier).archival_value
        if archival_value == ARCHIVAL_VALUE_UNWORTHY:
            return False
        elif archival_value == ARCHIVAL_VALUE_WORTHY:
            return True

        # sampling, unchecked, prompt
        return None

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

    def write_to_dossier(self, dossier):
        if self.get(dossier):
            ILifeCycle(dossier).archival_value = ARCHIVAL_VALUE_WORTHY

        else:
            ILifeCycle(dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY
