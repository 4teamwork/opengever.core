from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AddForm(TranslatedTitleAddForm):
    """Add form for opengever.meeting.committeecontainer."""


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(DefaultAddView):
    form = AddForm


class EditForm(TranslatedTitleEditForm):
    """Edit form for opengever.meeting.committeecontainer."""
