from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.meeting import is_word_meeting_implementation_enabled
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class CommitteContainerFieldConfigurationMixin(object):
    """Form mixin, configuring the avialable fields of committe container
    forms according to the feature flag configuration.
    """

    def updateFields(self):
        super(CommitteContainerFieldConfigurationMixin, self).updateFields()
        if is_word_meeting_implementation_enabled():
            self.fields = self.fields.omit('excerpt_template',
                                           'protocol_template')
        else:
            self.fields = self.fields.omit('ad_hoc_template',
                                           'paragraph_template',
                                           'protocol_header_template',
                                           'protocol_suffix_template')


class AddForm(CommitteContainerFieldConfigurationMixin, TranslatedTitleAddForm):
    """Add form for opengever.meeting.committeecontainer."""


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(DefaultAddView):
    form = AddForm


class EditForm(CommitteContainerFieldConfigurationMixin, TranslatedTitleEditForm):
    """Edit form for opengever.meeting.committeecontainer."""
