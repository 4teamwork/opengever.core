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
    """Correct cadwork mimetypes, which were not set correctly by the
    tus-upload.

    There could be others that were not set correctly, but it's hard to find
    out which. It would be limited to Cadwork as these mimetypes are not
    official IANA mimetypes.
    """

    deferrable = True

    def __call__(self):

        mtr = self.getToolByName('mimetypes_registry')

        for obj in self.objects(
            {
                'portal_type': 'opengever.document.document',
                'file_extension': CADWORK_EXTENSIONS,
            },
            'Correct Cadwork mimetypes'
        ):
            mt = mtr.lookupExtension(obj.file.filename)
            content_type = mt.mimetypes[0]
            if not obj.file.contentType == content_type:
                obj.file.contentType = content_type
                # Update catalog metadata (getContentType)
                # We also need getIcon for solr
                obj.reindexObject(idxs=['filename', 'getIcon'])
