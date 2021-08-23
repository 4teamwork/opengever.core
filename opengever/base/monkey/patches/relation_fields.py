from opengever.base.monkey.patching import MonkeyPatch


class PatchRelationFieldEventHandlers(MonkeyPatch):
    """Monkeypatch for z3c.relation.event._potential_relations

    This fixes an issue where event handlers would not work crrectly, notably
    to remove references from the catalog when an object is deleted.
    """

    def __call__(self):
        from plone.dexterity.utils import iterSchemata
        from z3c.relationfield.interfaces import IRelation
        from z3c.relationfield.interfaces import IRelationList
        from zope.schema import getFieldsInOrder

        def _potential_relations(obj):
            """Copy of z3c.relation.event._potential_relations, with the
            following modifications:
              - Make sure to iterate over all fields
              - use the interface to adapt the object when getting the field value
            """
            for schema in iterSchemata(obj):
                for name, field in getFieldsInOrder(schema):
                    if IRelation.providedBy(field):
                        try:
                            relation = getattr(obj, name)
                        except AttributeError:
                            # can't find this relation on the object
                            continue
                        yield name, None, relation
                    if IRelationList.providedBy(field):
                        try:
                            l = getattr(field.interface(obj), name)
                        except AttributeError:
                            # can't find the relation list on this object
                            continue
                        if l is not None:
                            for i, relation in enumerate(l):
                                yield name, i, relation

        from z3c.relationfield import event
        self.patch_refs(event, '_potential_relations', _potential_relations)
