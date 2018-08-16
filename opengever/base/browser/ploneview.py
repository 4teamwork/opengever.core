from plone import api
from Products.CMFPlone.browser.ploneview import Plone


class GeverPloneView(Plone):
    """Customize Ploneview's showEditableBorder, to include checks
    for workflow actions.
    """

    def showEditableBorder(self):
        request = self.request
        if 'disable_border' in request:
            return False

        value = super(GeverPloneView, self).showEditableBorder()

        # Also check for workflow actions, when the editable
        # border would be False
        if value is False:
            wftool = api.portal.get_tool('portal_workflow')
            if len(wftool.listActionInfos(object=self.context)):
                return True

        return value
