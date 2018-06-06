from ftw.upgrade import UpgradeStep
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from Products.CMFPlone.utils import base_hasattr
from zope.intid.interfaces import IIntIds


RELATION_FIELDS_TO_REMOVE = (
    'protocol_template',
    'excerpt_template',
)


class RemoveCommitteeAndCommitteecontainerFields(UpgradeStep):
    """Remove committee and committeecontainer fields.
    """

    def __call__(self):
        self.rel_catalog = getUtility(ICatalog)
        self.intids = getUtility(IIntIds)

        self.delete_committee_fields()
        self.delete_committee_container_fields()

    def delete_committee_fields(self):
        for committee in self.objects(
                {'portal_type': 'opengever.meeting.committee'},
                'Delete committee relation fields'):

            self.delete_relation_fields(committee)

    def delete_committee_container_fields(self):
        for committee_container in self.objects(
                {'portal_type': 'opengever.meeting.committeecontainer'},
                'Delete committee container relation fields'):

            self.delete_relation_fields(committee_container)

    def delete_relation_fields(self, obj):
        for field_name in RELATION_FIELDS_TO_REMOVE:
            if base_hasattr(obj, field_name):
                relation_value = getattr(obj, field_name)
                # find token (i.e. relation intid)
                token = self.intids.queryId(relation_value)
                # only remove realtion if token value is found
                # otherwise we assume the relation has not been entered into
                # the relation catalog for some reason unknown
                if token:
                    self.rel_catalog.unindex_doc(token)

                delattr(obj, field_name)
