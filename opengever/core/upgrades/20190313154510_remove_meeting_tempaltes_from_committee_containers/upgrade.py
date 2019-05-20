from ftw.upgrade import UpgradeStep
from opengever.meeting.committee import ICommittee
from opengever.meeting.committeecontainer import ICommitteeContainer
from z3c.relationfield.event import addRelations
from z3c.relationfield.relation import RelationValue
from zc.relation.interfaces import ICatalog
from zope import component
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


templates = [u'protocol_header_template',
             u'protocol_suffix_template',
             u'agenda_item_header_template',
             u'agenda_item_suffix_template',
             u'excerpt_header_template',
             u'excerpt_suffix_template',
             u'agendaitem_list_template',
             u'toc_template',
             u'paragraph_template']


class RemoveMeetingTempaltesFromCommitteeContainers(UpgradeStep):
    """Remove meeting templates from committee containers and make
    sure that the templates are set on the committees instead.
    """

    def __call__(self):
        relation_catalog = component.queryUtility(ICatalog)
        # First we make sure that templates are set on the committee
        query = {'object_provides': ICommittee.__identifier__}
        message = 'Make sure all meeting templates are set on the committee'
        intids = getUtility(IIntIds)
        for committee in self.objects(query, message):
            committee_container = committee.get_committee_container()
            for template_name in templates:
                if not getattr(committee, template_name, None) and getattr(committee_container, template_name, None):
                    template_relation = getattr(committee_container, template_name)
                    template = template_relation.to_object
                    if template:
                        setattr(committee, template_name, RelationValue(intids.getId(template)))
            committee.reindexObject()
            addRelations(committee, None)

        # Now we remove the relations to the templates on the ComitteeContainers
        # we can't use z3c.relationfield.eventremoveRelations because the fields
        # don't exist on the ICommitteeContainer schema anymore.
        # We also remove the attribute, as it will not be needed anymore
        query = {'object_provides': ICommitteeContainer.__identifier__}
        for committee_container in self.objects(query, message):
            for template_name in templates:
                if hasattr(committee_container, template_name):
                    template = getattr(committee_container, template_name)
                    if template:
                        relation_catalog.unindex(template)
                    delattr(committee_container, template_name)
