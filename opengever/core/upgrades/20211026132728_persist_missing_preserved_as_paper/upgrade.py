from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.base.default_values import object_has_value_for_field
from opengever.core.upgrade import DefaultValuePersister

preserved_as_paper = IDocumentMetadata.get("preserved_as_paper")


class PersistMissingPreservedAsPaper(UpgradeStep):
    """Persist missing preserved as paper default values.
    """

    deferrable = True

    def __call__(self):
        self.persist_preserved_as_paper()

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
