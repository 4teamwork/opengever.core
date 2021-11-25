from ftw.upgrade import UpgradeStep
from ftw.upgrade.interfaces import IUpgradeStepRecorder
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationMarker
from opengever.base.default_values import object_has_value_for_field
from opengever.core.upgrade import DefaultValuePersister
from zope.component import getMultiAdapter


classification = IClassification.get("classification")
privacy_layer = IClassification.get("privacy_layer")
public_trial = IClassification.get("public_trial")


class PersistMissingClassificationFields(UpgradeStep):
    """Persist missing classification fields default values.
    """

    deferrable = True
    ORIGINAL_UPGRADE_ID = '20211026132728'

    def __call__(self):
        if self.should_skip_upgrade():
            return

        self.persist_classification_fields()

    def should_skip_upgrade(self):
        """The upgrade 20211026132728 has been split into two separate steps.

        This upgrade 20211026132727 is introduced after the initial
        upgrade 20211026132728 has been released and potentially run on
        deployments.

        With the heuristic in this method we detect whether this upgrade should
        be run or skipped.

        Two cases are possible:
        - The upgrade 20211026132728 has already been installed. This means it
          has been installed in its previous version before the split and this
          new upgrade 20211026132727 should not be executed as it has already
          been executed as part of 20211026132728.
        - The upgrade 20211026132728 is not yet installed. This means we are
          installing the split versions of the upgrades for the first time and
          thus can go ahead with this upgrade.
        """
        recorder = getMultiAdapter(
            (self.portal, self.base_profile), IUpgradeStepRecorder
        )
        return recorder.is_installed(self.ORIGINAL_UPGRADE_ID)

    def persist_classification_fields(self):
        fields = (classification, privacy_layer, public_trial)
        with DefaultValuePersister(fields=fields) as persister:
            for obj in self.objects(
                {"object_provides": IClassificationMarker.__identifier__},
                "Persist Classification fields.",
            ):
                if all((object_has_value_for_field(obj, classification),
                        object_has_value_for_field(obj, privacy_layer),
                        object_has_value_for_field(obj, public_trial))):
                    continue
                persister.add_by_obj(obj)
