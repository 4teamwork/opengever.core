from opengever.base.monkey.patching import MonkeyPatch


class PatchRelationFieldEventHandlers(MonkeyPatch):
    """Monkeypatch for z3c.relation.event._potential_relations
    """

    def __call__(self):
        from z3c.relationfield.interfaces import IRelation
        from z3c.relationfield.interfaces import IRelationList
        from zope.interface import providedBy
        from zope.schema import getFields

        def _potential_relations(obj):
            """Copy of z3c.relation.event._potential_relations
            """
            for iface in providedBy(obj).flattened():
                for name, field in getFields(iface).items():
                    if IRelation.providedBy(field):
                        try:
                            relation = getattr(obj, name)
                        except AttributeError:
                            # can't find this relation on the object
                            continue
                        yield name, None, relation
                    if IRelationList.providedBy(field):
                        try:
                            l = getattr(obj, name)
                        except AttributeError:
                            # can't find the relation list on this object
                            continue
                        if l is not None:
                            for i, relation in enumerate(l):
                                yield name, i, relation

        from z3c.relationfield import event
        self.patch_refs(event, '_potential_relations', _potential_relations)
