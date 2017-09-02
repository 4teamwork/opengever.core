from ftw.upgrade import UpgradeStep


class EnableFtwKeywordwidgetAndIndexKeywordsOfDossiers(UpgradeStep):
    """Enable ftw.keywordwidget and index keywords of Dossiers.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.keywordwidget:default')
        self.setup_install_profile('profile-ftw.keywordwidget:select2js')

        # will be reindexed in 20170411113233
        # query = {'object_provides': [IDossierTemplateMarker.__identifier__,
        #                              IDossierMarker.__identifier__]}
        # self.catalog_reindex_objects(query, idxs=['Subject', ])
        self.install_upgrade_profile()
