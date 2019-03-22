from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.repository.interfaces import IRepositoryFolder
from zope.component import adapter
from zope.interface import Interface


@adapter(IRepositoryFolder, Interface)
class RepositoryFolderPostFactoryMenu(FilteredPostFactoryMenuWithWebactions):

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.meetingdossier':
            return True

        if factory_id == u'opengever.dossier.businesscasedossier' and \
                not self.context.allow_add_businesscase_dossier:
            return True
