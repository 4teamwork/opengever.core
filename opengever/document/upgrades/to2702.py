from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema


class AddMetadataBehaviorToDocumentFTI(UpgradeStep):
    """Add the IDocumentMetadata behavior to the og.document.document FTI.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.document.upgrades:2702')

        # XXX: Remove this check when merging upgrade-steps
        query = {'portal_type': 'opengever.document.document'}
        for doc in self.objects(query, 'Check document metadat  a'):
            print "Checking object %s" % doc.absolute_url()

            for name in IDocumentSchema.names():
                print "Checking attribute '%s'" % name
                getattr(doc, name)

            for name in IDocumentMetadata.names():
                print "Checking attribute '%s'" % name
                getattr(doc, name)
