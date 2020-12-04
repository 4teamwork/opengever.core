from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.archetypes import FolderZipRepresentation
from opengever.task.task import ITask
from plone import api
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class TaskZipRepresentation(FolderZipRepresentation):
    """Prevent adding empty tasks to the zip.

    This purposefully disregards `IZipExportSettings.include_empty_folders` and
    always omits empty tasks.

    If you're confused as to why this extends from
    `archetypes.FolderZipRepresentation` so am I. But apparently this
    representation adapter is also the default for dexterity folderish.
    """
    implements(IZipRepresentation)
    adapts(ITask, Interface)

    def get_files(self, path_prefix=u"", recursive=True, toplevel=True):
        query = {
            'object_provides': 'opengever.document.behaviors.IBaseDocument',
            'path': '/'.join(self.context.getPhysicalPath()),
        }
        if len(api.portal.get_tool('portal_catalog')(query)) == 0:
            return []

        return super(TaskZipRepresentation, self).get_files(
            path_prefix=path_prefix, recursive=recursive, toplevel=toplevel)
