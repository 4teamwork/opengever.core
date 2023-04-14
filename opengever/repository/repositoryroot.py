from opengever.base import _ as bmf
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.repository import _
from plone.app.content.interfaces import INameFromTitle
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer


class IRepositoryRoot(model.Schema):
    """ Repository root marker / schema interface
    """

    model.fieldset(
        u'common',
        label=bmf(u'fieldset_common', default=u'Common'),
        fields=[
            'valid_from',
            'valid_until',
            'version',
            'reference_number_addendum',
        ],
    )

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

    form.write_permission(reference_number_addendum='cmf.ManagePortal')
    reference_number_addendum = schema.TextLine(
        title=_(u'label_reference_number_addendum', default=u'Reference number addendum'),
        description=_(u'description_reference_number_addendum',
                      default=u'Attention: Change requires reindexing of "reference" '
                              u'and "sortable_reference".'),
        required=False,
    )


class RepositoryRoot(Container, TranslatedTitleMixin):
    """A Repositoryroot.
    """

    Title = TranslatedTitleMixin.Title

    # XXX - a dummy stub for the excel export
    def get_repository_number(self):
        return u''

    # XXX - a dummy stub for the excel export
    def get_retention_period(self):
        return u''

    # XXX - a dummy stub for the excel export
    def get_retention_period_annotation(self):
        return u''

    # XXX - a dummy stub for the excel export
    def get_archival_value(self):
        return u''

    # XXX - a dummy stub for the excel export
    def get_archival_value_annotation(self):
        return u''

    # XXX - a dummy stub for the excel export
    def get_custody_period(self):
        return u''


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
