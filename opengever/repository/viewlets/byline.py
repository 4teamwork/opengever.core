from opengever.base import _ as base_messagefactory
from opengever.base.viewlets.byline import BylineBase
from opengever.repository import _
from zope.i18n import translate


class RepositoryByline(BylineBase):

    def privacy_layer(self):
        return translate(self.context.privacy_layer,
                         context=self.request,
                         domain='opengever.base')

    def get_items(self):
        return [
            {'class': 'review_state',
             'label': _('label_workflow_state', default='State'),
             'content': self.workflow_state(),
             'replace': False},

            {'class': 'privacy_layer',
             'label': base_messagefactory(u'label_privacy_layer',
                                          default=u'Privacy layer'),
             'content': self.privacy_layer(),
             'replace': False},
        ]


class RepositoryRootByline(BylineBase):
    def get_items(self):
        return []
