from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.repository import _
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer


class IRepositoryRoot(model.Schema):
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


@implementer(INameFromTitle)
@adapter(IRepositoryRoot)
class RepositoryRootNameFromTitle(object):
    """ An INameFromTitle adapter for namechooser gets the name from the
    translated_title.
    """

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return ITranslatedTitle(self.context).translated_title()
