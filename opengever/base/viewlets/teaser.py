from opengever.base.interfaces import IGeverUI
from opengever.base.interfaces import ITeasersSettings
from opengever.ogds.models.user import User
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TeaserViewlet(ViewletBase):

    index = ViewPageTemplateFile('teaser.pt')

    tour_keys = ['be_new_frontend_teaser']

    def tours_to_show(self):
        userid = api.user.get_current().id
        ogds_user = User.query.filter_by(userid=userid).one_or_none()

        tours_to_show = []
        if ogds_user:
            seen_tours = ogds_user.user_settings.seen_tours if ogds_user.user_settings else []
            for key in self.tour_keys:
                if key not in seen_tours and key not in self.teasers_to_hide:
                    tours_to_show.append(key)

        return tours_to_show

    def is_ui_feature_enabled(self):
        return api.portal.get_registry_record(
            'is_feature_enabled', interface=IGeverUI)

    def show_viewlet(self):
        return api.portal.get_registry_record(
            'show_teasers', interface=ITeasersSettings)

    @property
    def teasers_to_hide(self):
        return api.portal.get_registry_record(
            'teasers_to_hide', interface=ITeasersSettings)
