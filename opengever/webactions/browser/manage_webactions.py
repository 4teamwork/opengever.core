from collections import OrderedDict
from opengever.base.utils import escape_html
from opengever.webactions.storage import get_storage
from plone import api
from Products.Five import BrowserView


class ManageWebactionsView(BrowserView):

    _attributes_not_to_escape = ['action_id', 'created', 'display', 'enabled',
                                 'groups', 'mode', 'modified',
                                 'order', 'owner', 'permissions',
                                 'scope', 'types']

    def __call__(self):
        if 'action-delete-webactions' in self.request.form:
            return self.delete_selected_webactions()

        self.request.set('disable_border', True)
        return self.index()

    @property
    def main_url(self):
        return self.context.absolute_url() + '/@@manage-webactions'

    def _get_webactions(self):
        if 'Manager' in api.user.get_roles():
            # Manager may always list all actions
            return get_storage().list()
        else:
            # Other users may only see their own
            return get_storage().list(owner=api.user.get_current().id)

    def get_webactions_data(self):
        return map(self._prepare_webaction, self._get_webactions())

    def _sort_data(self, items):
        field_order = {"unique_name": 1,
                       "owner": 2,
                       "comment": 3,
                       "target_url": 4,
                       "created": 5,
                       "modified": 6,
                       "display": 7,
                       "order": 8,
                       }
        return sorted(items, key=lambda item: field_order.get(item[0], 20))

    def _filter_data(self, items):
        return filter(self._filter_webaction_data, items)

    @staticmethod
    def _filter_webaction_data(item):
        key, value = item
        if key in ["title", "action_id"]:
            return False
        return True

    @staticmethod
    def _format_field(fieldname, value):
        if fieldname == 'icon_data':
            return u'<img src="{}" />'.format(value)
        elif fieldname == 'icon_name':
            return u'<span>{0} (<span class="fa {0}"/>)</span>'.format(value)
        elif fieldname == 'target_url':
            return u'<a href={0}>{0}</a>'.format(value)
        elif fieldname in ["created", "modified"]:
            return value.strftime('%d.%m.%Y %H:%M')
        return value

    def _escape_html(self, action):
        return {key: value if key in self._attributes_not_to_escape
                else escape_html(value) for key, value in action.items()}

    def _prepare_webaction(self, action):
        # first we html escape the data
        action = self._escape_html(action)

        data = {}
        data["action_id"] = action["action_id"]
        data["title"] = action["title"]
        data["edit_url"] = "/".join(
            [self.context.absolute_url(),
             "@@manage-webactions-edit?action_id={}".format(action["action_id"])])
        data["other-fields"] = OrderedDict()

        for field, value in self._sort_data(self._filter_data(action.items())):
            data["other-fields"][field] = self._format_field(field, value)
        return data

    def delete_selected_webactions(self):
        selected_webactions = self.request.form.get('selected_webactions', [])
        storage = get_storage()
        for action_id in selected_webactions:
            storage.delete(int(action_id))
        return self.request.RESPONSE.redirect(self.main_url)
