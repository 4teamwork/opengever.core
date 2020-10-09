from ftw.upgrade import UpgradeStep


class AddPhvsSpecialFieldsToSolr(UpgradeStep):
    """Add phvs special fields to solr.
    """

    deferrable = True

    marker_interface = "opengever.phvs.behaviors.IPHVSAdditionalBehaviorMarker"

    def __call__(self):
        query = {'object_provides': self.marker_interface}
        for obj in self.objects(query, 'Index phvs special fields in solr.'):
            obj.reindexObject(idxs=['language', 'location'])
