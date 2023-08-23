from collections import OrderedDict
from opengever.ogds.models.service import ogds_service


class InitialContentFactory(object):

    INBOX_CONTAINER_GUID = "inbox-container"
    PRIVATE_ROOT_GUID = "private-root"
    TEMPLATE_FOLDER_GUID = "template-folder"

    TOP_LEVEL_INBOX_ID = "eingangskorb"
    TEMPLATE_FOLDER_ID = "vorlagen"
    PRIVATE_ROOT_ID = "private"

    def __init__(self):
        self.org_units = ogds_service().all_org_units()

    def generate(self, bundle_content_counts):
        """Produce OGGBundle items for initial content.

        This will return inital content items for inbox containers, inboxes,
        private roots and template folders that can be injected into the
        bundle transmogrifier pipeline.

        Only content for types that are not already contained in the bundle,
        according to the stats in `bundle_content_counts`, will be produced.

        The generated content is dynamic and based on the existing OrgUnits.
        """
        content = OrderedDict()

        # Order matters here - parents before children
        if not bundle_content_counts.get('inboxcontainers.json', 0):
            content['inboxcontainers.json'] = self._generate_inbox_containers()

        if not bundle_content_counts.get('inboxes.json', 0):
            content['inboxes.json'] = self._generate_inboxes()

        if not bundle_content_counts.get('privateroots.json', 0):
            content['privateroots.json'] = self._generate_private_roots()

        if not bundle_content_counts.get('templatefolders.json', 0):
            content['templatefolders.json'] = self._generate_template_folders()

        return content

    def _generate_inbox_containers(self):
        if len(self.org_units) == 1:
            # Only one OU. Create inbox directly at top level, no container.
            return []

        elif len(self.org_units) > 1:
            # Multiple OUs. Create an inbox container.
            all_inbox_groups = [ou.inbox_group_id for ou in self.org_units]

            inbox_containers = [{
                "guid": self.INBOX_CONTAINER_GUID,
                "_id": self.TOP_LEVEL_INBOX_ID,
                "review_state": "inbox-state-default",
                "title_de": "Eingangskorb",
                "title_fr": 'Bo\xc3\xaete de r\xc3\xa9ception',
                "title_en": "Inbox",
                "_permissions": {
                    "read": all_inbox_groups,
                }
            }]
            return inbox_containers

        else:
            # No OUs. Probably a malformed bundle.
            return []

    def _generate_inboxes(self):
        if len(self.org_units) == 1:
            # Only one OU. Create inbox directly at top level, no container.
            ou = self.org_units[0]

            # Not setting either a parent_guid or parent_reference will cause
            # the inbox to be rooted to the Plone site.
            inboxes = [{
                "guid": "inbox-%s" % ou.unit_id,
                "_id": self.TOP_LEVEL_INBOX_ID,
                "review_state": "inbox-state-default",
                "title_de": "Eingangskorb",
                "title_fr": "Bo\xc3\xaete de r\xc3\xa9ception",
                "title_en": "Inbox",
                "responsible_org_unit": ou.unit_id,
                "_permissions": {
                    "read": [
                        ou.inbox_group_id
                    ],
                    "add": [
                        ou.inbox_group_id
                    ],
                    "edit": [
                        ou.inbox_group_id
                    ]
                }
            }]
            return inboxes

        elif len(self.org_units) > 1:
            inboxes = []

            for ou in self.org_units:
                title_de = u'Eingangskorb %s' % ou.title
                title_fr = u'Bo\xeete de r\xe9ception %s' % ou.title
                title_en = u'Inbox %s' % ou.title

                inbox = {
                    "guid": "inbox-%s" % ou.unit_id,
                    "parent_guid": self.INBOX_CONTAINER_GUID,
                    "_id": ou.unit_id,
                    "review_state": "inbox-state-default",
                    "title_de": title_de,
                    "title_fr": title_fr,
                    "title_en": title_en,
                    "responsible_org_unit": ou.unit_id,
                    "_permissions": {
                        "block_inheritance": True,
                        "read": [
                            ou.inbox_group_id
                        ],
                        "add": [
                            ou.inbox_group_id
                        ],
                        "edit": [
                            ou.inbox_group_id
                        ]
                    }
                }
                inboxes.append(inbox)

            return inboxes

        else:
            # No OUs. Probably a malformed bundle.
            return []

    def _generate_private_roots(self):
        private_roots = [
            {
                "guid": self.PRIVATE_ROOT_GUID,
                "_id": self.PRIVATE_ROOT_ID,
                "review_state": "repositoryroot-state-active",  # [sic]
                "title_de": "Meine Ablage",
                "title_fr": "Dossier personnel",
                "title_en": "My repository",
            }
        ]
        return private_roots

    def _generate_template_folders(self):
        all_inbox_groups = [ou.inbox_group_id for ou in self.org_units]
        all_users_groups = [ou.users_group_id for ou in self.org_units]

        template_folders = [
            {
                "guid": self.TEMPLATE_FOLDER_GUID,
                "_id": self.TEMPLATE_FOLDER_ID,
                "review_state": "templatefolder-state-active",
                "title_de": "Vorlagen",
                "title_fr": "Mod\xc3\xa8les",
                "title_en": "Templates",
                "_permissions": {
                    "read": all_users_groups,
                    "add": all_inbox_groups,
                    "edit": all_inbox_groups,
                }
            }
        ]
        return template_folders
