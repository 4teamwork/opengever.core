from ftw.upgrade import UpgradeStep
from OFS.interfaces import IOrderedContainer
from plone import api
from plone.dexterity.utils import createContentInContainer
import logging


log = logging.getLogger('opengever.inbox')


class ConvertMainInboxes(UpgradeStep):

    def __call__(self):

        if not self.is_setup_with_subinboxes():
            log.warn('ConvertMainInboxes upgradestep skipped,'
                     'because it is not an setup with multiptle subinboxes')
            return

        main_inbox = self.get_main_inbox()
        local_roles = main_inbox.get_local_roles()
        position = IOrderedContainer(self.portal).getObjectPosition(
            main_inbox.getId())

        # create temp container and move inbox-content inside
        temp_container = createContentInContainer(
            self.portal,
            'opengever.inbox.container',
            title=u'Temp. Eingangskorb')

        self.move_all_items(source_container=main_inbox, target=temp_container)

        self.safe_delete(main_inbox)

        # create real inbox container and move temp-content inside
        inbox_container = createContentInContainer(
            self.portal,
            'opengever.inbox.container',
            id='eingangskorb',
            title=u'Eingangskorb')

        self.move_all_items(source_container=temp_container,
                            target=inbox_container)

        self.safe_delete(temp_container)

        # readd the local roles
        for principal, roles in local_roles:
            roles_list = [item for item in roles]
            inbox_container.manage_setLocalRoles(principal, roles_list)
            inbox_container.reindexObjectSecurity()

        # set original position
        self.portal.moveObject(inbox_container.getId(), position)

    def safe_delete(self, obj):
        if len(obj.listFolderContents()) != 0:
            raise RuntimeError('{} is not empty, but all contents '
                               'should moved away'.format(obj.Title()))

        api.content.delete(obj=obj)

    def move_all_items(self, source_container=None, target=None):
        for item in source_container.listFolderContents():
            api.content.move(source=item, target=target)

    def is_setup_with_subinboxes(self):
        main_inbox = self.get_main_inbox()
        if main_inbox:
            sub_inboxes = main_inbox.listFolderContents(
                {'portal_type': 'opengever.inbox.inbox'})

            if len(sub_inboxes) > 0:
                return True

        return False

    def get_main_inbox(self):
        inboxes = self.portal.listFolderContents(
            {'portal_type': 'opengever.inbox.inbox'})
        if inboxes:
            return inboxes[0]

        return None
