from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.repository import _
from plone.directives import form
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces import NotFound
import re


class IRepositoryRoot(form.Schema):
    """ Repository root marker / schema interface
    """

    valid_from = schema.Date(
        title=_(u'label_valid_from', default=u'Valid from'),
        description=_(u'help_valid_from', default=u''),
        required=False,
        )

    valid_until = schema.Date(
        title=_(u'label_valid_until', default=u'Valid until'),
        description=_(u'help_valid_until', default=u''),
        required=False,
        )

    version = schema.TextLine(
        title=_(u'label_version', default=u'Version'),
        description=_(u'help_version', default=''),
        required=False,
        )


def zero_fill(matchobj):
    return matchobj.group().zfill(6)

num_sort_regex = re.compile('\d+')


class PrimaryRepositoryRoot(grok.View):
    """A simple view for finding the primary repository root.
    """

    grok.context(Interface)
    grok.name('primary_repository_root')
    grok.require('zope2.View')

    def render(self):
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
