from five import grok
from opengever.tabbedview.browser.listing import ListingView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig, ITableSource
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import linked_ogds_author
from persistent.list import PersistentList
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.globalrequest import getRequest
from zope.i18nmessageid.message import Message
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.schema.vocabulary import getVocabularyRegistry
import base64


@ram.cache(lambda method, role: role)
def translate_participation_role(role):
    site = getSite()
    vr = getVocabularyRegistry()
    vocab = vr.get(site, 'opengever.dossier.participation_roles')

    try:
        term = vocab.getTerm(role)
    except LookupError:
        return role
    else:
        return term.title


def role_list_helper(item, value):
    """ Format list of roles.
    """

    if isinstance(value, Message):
        # translate the message
        return translate(value, context=getRequest())

    elif sum([int(isinstance(value, t)) for t in (str, unicode)]):
        # is it a string or unicode or a subtype of them?
        return translate_participation_role(value)

    elif sum([int(isinstance(value, t)) for t in (list, tuple, set,
                                                  PersistentList)]):
        # if it's a list, lets iterate over it
        translated_values = []
        for role in value:
            translated_values.append(translate_participation_role(role))
        return ', '.join(translated_values)

    else:
        return value


def icon_helper(item, value):
    return "<span class='function-user'>&nbsp;</span>"


def base64_oid_checkbox_helper(item, value):
    if not getattr(item, '_p_oid', False):
        attrs = {'type': 'checkbox',
                 'disabled': 'disabled',
                 'class': 'noborder'}
    else:
        oid = base64.encodestring(item._p_oid).strip()
        attrs = {
            'type': 'checkbox',
            'class': 'noborder selectable',
            'name': 'oids:list',
            'id': 'item-%s' % oid,
            'value': oid,
            }
    html = '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                      for k, v in attrs.items()])
    return html


class IParticipationSourceConfig(ITableSourceConfig):
    """Marker interface for a participation table source config.
    """


class Participants(grok.View, OpengeverTab, ListingView):
    """ Participants listing tab for dossiers using the
    IParticipantsAware behavior
    """

    implements(IParticipationSourceConfig)

    grok.require('zope2.View')
    grok.name('tabbedview_view-participants')
    grok.context(IParticipationAwareMarker)

    select_all_template = ViewPageTemplateFile(
        'templates/select_all_participants.pt')
    sort_on = 'Contact'

    columns = (

        ('', base64_oid_checkbox_helper, ),
        ('', icon_helper, ),

        {'column': 'contact',
         'column_title': _(u'column_contact', default=u'Contact'),
         'transform': linked_ogds_author},

        {'column': 'roles',
         'column_title': _(u'column_rolelist', default=u'role_list'),
         'transform': role_list_helper},

        )

    def create_id(self, item):
        if not getattr(item, '_p_oid', False):
            return ''
        return base64.encodestring(item._p_oid).strip()

    enabled_actions = [
        'delete_participants',
        'add_participant',
        'reset_tableconfiguration',
        ]

    major_actions = [
        'delete_participants',
        'add_participant',
        ]

    def get_base_query(self):
        return None

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class ParticipantsTableSource(grok.MultiAdapter, BaseTableSource):
    """
    """

    grok.implements(ITableSource)
    grok.adapts(IParticipationSourceConfig, Interface)

    def validate_base_query(self, query):
        """hacky: get the actual elements here because we are not
        able to use queries on annotations / lists ...
        """

        context = self.config.context

        phandler = IParticipationAware(context)
        results = list(phandler.get_participations())

        dossier_adpt = IDossier(context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append({'contact': dossier_adpt.responsible,
                        'roles': responsible_name,
                        'role_list': responsible_name,
                        'locked': True,  # not deletable
                        })

        return results

    def extend_query_with_ordering(self, results):
        if self.config.sort_on:
            sorter = lambda a, b: cmp(getattr(a, self.config.sort_on, ''),
                                      getattr(b, self.config.sort_on, ''))
            results.sort(sorter)

        if self.config.sort_on and self.config.sort_reverse:
            results.reverse()

        return results

    def extend_query_with_textfilter(self, results, text):
        if not len(text):
            return results

        if text.endswith('*'):
            text = text[:-1]

        def _search_method(participation):
            # roles
            if text.lower() in role_list_helper(
                participation, participation.roles).lower():
                return True

            if text.lower() in readable_ogds_author(
                participation, participation.contact):
                return True

            return False

        results = filter(_search_method, results)

        return results

    def search_results(self, results):
        return results
