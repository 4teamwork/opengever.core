from ftw.upgrade import UpgradeStep

ONENOTE_EXTENSIONS = ['.one']


class UpdateOneNoteMimetype(UpgradeStep):
    """Update one note mimetype.
    """

    def __call__(self):
        self.install_upgrade_profile()

        mtr = self.getToolByName('mimetypes_registry')

        for obj in self.objects(
            {
                'portal_type': 'opengever.document.document',
                'file_extension': ONENOTE_EXTENSIONS,
            },
            'Set OneNote mimetypes'
        ):
            mt = mtr.lookupExtension(obj.file.filename)
            content_type = mt.mimetypes[0]
            if obj.file.contentType != content_type:
                obj.file.contentType = content_type
                # Update catalog metadata (getContentType)
                obj.reindexObject(idxs=['filename'])
