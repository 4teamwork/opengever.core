from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.meeting import is_word_meeting_implementation_enabled
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AddForm(TranslatedTitleAddForm):
    """Add form for opengever.meeting.committeecontainer."""

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()

        if not is_word_meeting_implementation_enabled():
            self.widgets['ad_hoc_template'].mode = HIDDEN_MODE
            self.widgets['paragraph_template'].mode = HIDDEN_MODE
            self.widgets['protocol_header_template'].mode = HIDDEN_MODE
            self.widgets['protocol_suffix_template'].mode = HIDDEN_MODE
        else:
            self.widgets['excerpt_template'].mode = HIDDEN_MODE
            self.widgets['protocol_template'].mode = HIDDEN_MODE


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(DefaultAddView):
    form = AddForm


class EditForm(TranslatedTitleEditForm):
    """Edit form for opengever.meeting.committeecontainer."""

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()

        if not is_word_meeting_implementation_enabled():
            self.widgets['ad_hoc_template'].mode = HIDDEN_MODE
            self.widgets['paragraph_template'].mode = HIDDEN_MODE
            self.widgets['protocol_header_template'].mode = HIDDEN_MODE
            self.widgets['protocol_suffix_template'].mode = HIDDEN_MODE
        else:
            self.widgets['excerpt_template'].mode = HIDDEN_MODE
            self.widgets['protocol_template'].mode = HIDDEN_MODE
