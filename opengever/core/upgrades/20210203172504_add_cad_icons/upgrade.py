from ftw.upgrade import UpgradeStep


CAD_EXTENSIONS = [
    '.2d',
    '.2dr',
    '.dwg',
    '.dxf',
]


class AddCADIcons(UpgradeStep):
    """Add cad icons.
    """

    def __call__(self):
        self.install_upgrade_profile()

        for obj in self.objects(
            {
                'portal_type': 'opengever.document.document',
                'file_extension': CAD_EXTENSIONS,
            },
            'Reindex getIcon'
        ):
            # Update catalog metadata getIcon
            # Reindexing getId to avoid reindexing all indexes in portal catalog
            obj.reindexObject(idxs=['getIcon', 'getId'])
