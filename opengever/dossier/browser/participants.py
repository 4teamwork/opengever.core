from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.ogds.base.actor import Actor
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import GeverTableSource
from opengever.tabbedview.helper import readable_ogds_author
from persistent.list import PersistentList
from plone.memoize import ram
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
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

    elif any([isinstance(value, t) for t in (str, unicode)]):
        # is it a string or unicode or a subtype of them?
        return translate_participation_role(value)

    elif any([isinstance(value, t) for t in (list, tuple, set,
                                             PersistentList)]):
        # if it's a list, lets iterate over it
        translated_values = []
        for role in value:
            translated_values.append(translate_participation_role(role))
        return ', '.join(translated_values)

    else:
        return value


def linked_ogds_author_with_icon(item, author):
    return Actor.lookup(author).get_link(with_icon=True)


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


class Participants(BaseListingTab):
    """ Participants listing tab for dossiers using the
    IParticipantsAware behavior
    """

    implements(IParticipationSourceConfig)

    select_all_template = ViewPageTemplateFile(
        'templates/select_all_participants.pt')
    sort_on = 'Contact'

    columns = (

        {'column': '',
         'transform': base64_oid_checkbox_helper,
         'width': 25},

        {'column': 'contact',
         'column_title': _(u'column_contact', default=u'Contact'),
         'transform': linked_ogds_author_with_icon},

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
    ]

    major_actions = [
        'delete_participants',
        'add_participant',
    ]

    def get_base_query(self):
        return None


class ParticipationResponsible(object):
    """Temporary participant to also display the dossier-repsonsible in the
    participants tab.

    """
    def __init__(self, contact, responsible):
        self.locked = True
        self.roles = responsible
        self.role_list = responsible
        self.contact = contact


@implementer(ITableSource)
@adapter(IParticipationSourceConfig, Interface)
class ParticipantsTableSource(GeverTableSource):

    def validate_base_query(self, query):
        """hacky: get the actual elements here because we are not
        able to use queries on annotations / lists ...
        """
        context = self.config.context

        phandler = IParticipationAware(context)
        results = list(phandler.get_participations())

        dossier_adpt = IDossier(context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append(ParticipationResponsible(
            contact=dossier_adpt.responsible,
            responsible=responsible_name))

        return results

    def extend_query_with_ordering(self, results):
        if self.config.sort_on:
            results.sort(
                key=lambda x: getattr(x, self.config.sort_on, ''),
                reverse=self.config.sort_reverse,
            )

        return results

    def extend_query_with_textfilter(self, results, text):
        if not len(text):
            return results

        if text.endswith('*'):
            text = text[:-1]

        def _search_method(participation):
            if text.lower() in role_list_helper(
                    participation, participation.roles).lower():
                return True

            if text.lower() in readable_ogds_author(
                    participation, participation.contact).lower():
                return True

            return False

        results = filter(_search_method, results)

        return results

    def search_results(self, results):
        return results
