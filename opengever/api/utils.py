
def raise_for_api_request(request, exc):
    if not request.get("error_as_message"):
        raise exc


def get_obj_by_path(portal, path):
    """restrictedTraverse checks all of the objects along the path are
    validated with the security machinery. But we only need to know if the
    user is able to access the given object.

    Used by RelationChoiceFieldDeserializer and Copy service customization.
    """

    path = path.rstrip('/').split('/')
    parent = portal.unrestrictedTraverse(path[:-1], None)
    if not parent:
        return None

    return parent.restrictedTraverse(path[-1], None)
