from opengever.ogds.base.sync.ogds_updater import sync_ogds
from plone.restapi.services import Service


class OgdsSync(Service):

    def reply(self):
        sync_ogds(
            self.context, users=True, groups=True, local_groups=True)

        self.request.response.setStatus(204)
        return super(OgdsSync, self).reply()
