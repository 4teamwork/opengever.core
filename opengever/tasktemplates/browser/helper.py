from opengever.tabbedview.helper import readable_ogds_author
from opengever.tasktemplates.vocabularies import interactive_users
from plone.memoize import ram


@ram.cache(lambda m, i, author: author)
def interactive_user_helper(item, value):
    """Helper method for `ftw.table` which is able to translate the
    available interactive users (from vocabluaries) or effective OGDS
    users.
    """

    # create a interactive users mapping
    iuser_map = dict(interactive_users({}))
    # is it a interactive user?
    if value in iuser_map:
        return iuser_map.get(value)

    # fall back to OGDS helper
    else:
        return readable_ogds_author(item, value)
