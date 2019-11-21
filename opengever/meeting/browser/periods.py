from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.tabbedview import GeverTabMixin
from plone import api
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class PeriodEditForm(DefaultEditForm):

    def nextURL(self):
        # context of edit form is period, so get parent committee first
        return aq_parent(aq_inner(self.context)).absolute_url() + '#periods'


class PeriodAddForm(DefaultAddForm):

    def nextURL(self):
        # context of add form is committee
        return self.context.absolute_url() + '#periods'


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class PeriodAddView(DefaultAddView):
    form = PeriodAddForm


class PeriodsTab(BrowserView, GeverTabMixin):

    show_searchform = False

    template = ViewPageTemplateFile('templates/periods.pt')

    def __call__(self):
        return self.template()

    def get_periods(self):
        """Returns all periods for the current committee.
        """
        return api.content.find(
            context=self.context,
            portal_type='opengever.meeting.period',
            sort_on='start',
            sort_order='descending')

    def get_localized_time(self, dt):
        return api.portal.get_localized_time(datetime=dt)

    def is_editable_by_current_user(self):
        """Return whether the current user can edit periods."""

        return api.user.has_permission(
            'Modify portal content', obj=self.context)

    def is_manager(self):
        return api.user.has_permission('cmf.ManagePortal')
