from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.publisher.interfaces import NotFound
import re


num_sort_regex = re.compile(r'\d+')


def zero_fill(matchobj):
    return matchobj.group().zfill(6)


class PrimaryRepositoryRoot(BrowserView):
    """A simple view for finding the primary repository root.
    """

    def __call__(self):
        root = self.get_primary_repository_root()
        return self.request.RESPONSE.redirect(root.absolute_url())

    def get_primary_repository_root(self):
        """The primary repository root is usally the repository root found
        in the plone site with the biggets postfix number.
        """

        site = getToolByName(self.context, 'portal_url').getPortalObject()
        query = {'portal_type': ['opengever.repository.repositoryroot']}
        brains = site.getFolderContents(full_objects=True,
                                        contentFilter=query)

        if len(brains) == 0:
            raise NotFound(site, 'repository-root', self.request)

        def sorter(a, b):
            """Sorts by id, replacing numbers with zero filled numbers.
            """
            a_id = num_sort_regex.sub(zero_fill, a.id)
            b_id = num_sort_regex.sub(zero_fill, b.id)
            return cmp(a_id, b_id)

        brains.sort(sorter)

        return brains[-1]
