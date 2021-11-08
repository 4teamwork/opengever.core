from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationMarker
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.base.default_values import object_has_value_for_field
from opengever.core.upgrade import DefaultValuePersister

classification = IClassification.get("classification")
privacy_layer = IClassification.get("privacy_layer")
public_trial = IClassification.get("public_trial")
preserved_as_paper = IDocumentMetadata.get("preserved_as_paper")


class PersistMissingDefaultValues(UpgradeStep):
    """Persist missing default values.
    """

    deferrable = True

    def __call__(self):
        self.persist_classification_fields()
        self.persist_preserved_as_paper()

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

    def persist_preserved_as_paper(self):
        fields = (preserved_as_paper, )
        with DefaultValuePersister(fields=fields) as persister:
            for obj in self.objects(
                {"object_provides": IDocumentMetadata.__identifier__},
                "Persist preserved_as_paper.",
            ):
                if object_has_value_for_field(obj, preserved_as_paper):
                    continue
                persister.add_by_obj(obj)
