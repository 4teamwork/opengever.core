from opengever.ogds.models.user import User
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TeaserViewlet(ViewletBase):

    index = ViewPageTemplateFile('teaser.pt')

    tour_keys = ['be_new_frontend_teaser']

    def unseen_tours(self):
        userid = api.user.get_current().id
        ogds_user = User.query.filter_by(userid=userid).one_or_none()
        unseen_tours = []
        if ogds_user:
            seen_tours = ogds_user.user_settings.seen_tours if ogds_user.user_settings else []
            for key in self.tour_keys:
                if key not in seen_tours:
                    unseen_tours.append(key)
        return unseen_tours
