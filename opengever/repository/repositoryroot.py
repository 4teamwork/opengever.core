from five import grok
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.repository import _
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity.content import Container
from plone.directives import form
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces import NotFound
import re


class IRepositoryRoot(form.Schema):
    """ Repository root marker / schema interface
    """

    valid_from = schema.Date(
        title=_(u'label_valid_from', default=u'Valid from'),
        required=False,
        )

    valid_until = schema.Date(
        title=_(u'label_valid_until', default=u'Valid until'),
        required=False,
        )

    version = schema.TextLine(
        title=_(u'label_version', default=u'Version'),
        required=False,
        )


class RepositoryRoot(Container, TranslatedTitleMixin):
    """A Repositoryroot.
    """

    Title = TranslatedTitleMixin.Title


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


class RepositoryRootNameFromTitle(grok.Adapter):
    """ An INameFromTitle adapter for namechooser gets the name from the
    translated_title.
    """
    grok.implements(INameFromTitle)
    grok.context(IRepositoryRoot)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return ITranslatedTitle(self.context).translated_title()
