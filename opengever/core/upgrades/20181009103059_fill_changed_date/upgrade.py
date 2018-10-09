from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.changed import METADATA_CHANGED_FILLED_KEY
from opengever.base.behaviors.changed import IChanged
from zope.annotation import IAnnotations
from zope.component.hooks import getSite


types_with_changed = ['ftw.mail.mail',
                      'opengever.contact.contact',
                      'opengever.disposition.disposition',
                      'opengever.document.document',
                      'opengever.dossier.businesscasedossier',
                      'opengever.dossier.dossiertemplate',
                      'opengever.inbox.forwarding',
                      'opengever.inbox.inbox',
                      'opengever.inbox.yearfolder',
                      'opengever.meeting.committee',
                      'opengever.meeting.meetingdossier',
                      'opengever.meeting.meetingtemplate',
                      'opengever.meeting.paragraphtemplate',
                      'opengever.meeting.proposal',
                      'opengever.meeting.proposaltemplate',
                      'opengever.meeting.sablontemplate',
                      'opengever.meeting.submittedproposal',
                      'opengever.private.dossier',
                      'opengever.repository.repositoryfolder',
                      'opengever.task.task',
                      'opengever.tasktemplates.tasktemplate',
                      'opengever.tasktemplates.tasktemplatefolder',
                      'opengever.workspace.folder',
                      'opengever.workspace.workspace']

query = {'portal_type': types_with_changed}


class FillChangedMetadata(UpgradeStep):
    """Set the changed field on the objects, then reindex the changed index
    and update the metadata changed column
    """

    deferrable = True

    def __call__(self):
        self.fill_changed_field()
        self.reindex_changed_index()
        self.set_changed_flag()

    def fill_changed_field(self):
        """Set the 'changed' field on the object if it hasn't been set already"""
        for obj in self.objects(query, 'Initialize IChanged.changed field values'):
            if not obj.changed:
                IChanged(obj).changed = obj.modified()

    def reindex_changed_index(self):
        """We first need to clear the index, as it was also set for objects
        that do not have the IChanged behavior when we copied the
        modified index. This also fills the metadata column.
        """
        catalog = self.getToolByName('portal_catalog')
        changed_index = catalog._catalog.indexes["changed"]
        changed_index.clear()
        self.catalog_reindex_objects(query, idxs=["changed", "object_provides"])

    def set_changed_flag(self):
        site = getSite()
        annotations = IAnnotations(site)
        annotations[METADATA_CHANGED_FILLED_KEY] = True
