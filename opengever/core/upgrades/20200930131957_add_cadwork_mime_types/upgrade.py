from ftw.upgrade import UpgradeStep


CADWORK_EXTENSIONS = [
    '.2d',
    '.2dc',
    '.2dl',
    '.2dm',
    '.2dr',
    '.3d',
    '.3dc',
    '.iv',
    '.ivx',
    '.ivz',
    '.l2d',
    '.lx2d',
    '.lxz',
]


class AddCadworkMimeTypes(UpgradeStep):
    """Add cadwork mime types.
    """

    def __call__(self):
        self.install_upgrade_profile()

        mtr = self.getToolByName('mimetypes_registry')

        for obj in self.objects(
            {
                'portal_type': 'opengever.document.document',
                'file_extension': CADWORK_EXTENSIONS,
            },
            'Set Cadwork mimetypes'
        ):
            mt = mtr.lookupExtension(obj.file.filename)
            obj.file.contentType = mt.mimetypes[0]
            # Update catalog metadata (getContentType)
            obj.reindexObject(idxs=['filename'])
