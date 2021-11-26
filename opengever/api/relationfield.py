from opengever.api.utils import get_obj_by_path
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.oguid import Oguid
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.relationfield import RelationChoiceFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.interfaces import IRelationChoice
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
import six


def relationfield_value_to_object(value, context, request):
    if isinstance(value, dict):
        # We are trying to deserialize the output of a serialization
        # which is enhanced, extract it and put it on the loop again
        value = value["@id"]

    if isinstance(value, int):
        # Resolve by intid
        intids = queryUtility(IIntIds)
        return intids.queryObject(value), "intid"
    elif isinstance(value, six.string_types):
        if six.PY2 and isinstance(value, six.text_type):
            value = value.encode("utf8")
        portal = getMultiAdapter(
            (context, request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()
        if value.startswith(portal_url):
            # Resolve by URL
            return get_obj_by_path(portal, value[len(portal_url) + 1:]), "URL"
        elif value.startswith("/"):
            # Resolve by path
            return get_obj_by_path(portal, value.lstrip("/")), "path"
        elif Oguid.is_oguid(value):
            # Resolve by OGUID
            return Oguid.parse(value).resolve_object(), "oguid"
        else:
            # Resolve by UID
            catalog = getToolByName(context, "portal_catalog")
            brain = catalog(UID=value)
            if brain:
                return brain[0].getObject(), "UID"

        return None, "UID"


@implementer(IFieldDeserializer)
@adapter(IRelationChoice, IDexterityContent, IOpengeverBaseLayer)
class GeverRelationChoiceFieldDeserializer(RelationChoiceFieldDeserializer):
    """Customize the RelationFieldDeserializer to fix a problem when
    referencing objects by the path or URL and not the complete path is
    accessible for the current user.
    """

    def __call__(self, value):
        """Copied from the baseclass"""

        obj, resolved_by = relationfield_value_to_object(
            value, self.context, self.request)
        if obj is None:
            self.request.response.setStatus(400)
            raise ValueError(
                u"Could not resolve object for {}={}".format(resolved_by, value)
            )

        self.field.validate(obj)
        return obj
