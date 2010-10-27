import base64

from five import grok
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.helper import readable_ogds_author
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier import _
from zope.schema.vocabulary import getVocabularyRegistry
from zope.app.component.hooks import getSite
from zope.i18nmessageid.message import Message
from plone.memoize import ram
from persistent.list import PersistentList


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
        site = getSite()
        return site.translate(value)

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


class Participants(OpengeverListingTab):
    """ Participants listing tab for dossiers using the
    IParticipantsAware behavior
    """
    grok.name('tabbedview_view-participants')
    grok.context(IParticipationAwareMarker)

    def base64_oid_checkbox(item, value):
        if not getattr(item, '_p_oid', False):
            return ''
        oid = base64.encodestring(item._p_oid)
        attrs = {
            'type': 'checkbox',
            'class': 'noborder',
            'name': 'oids:list',
            'id': 'item-%s' % oid,
            'value': oid,
            }
        html = '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                          for k, v in attrs.items()])
        return html

    def icon_helper(item, value):
        return '<img src="user.gif" alt="" title="" border="0" />'

    sort_on = 'Contact'

    columns = (

        ('', base64_oid_checkbox, ),
        ('', icon_helper, ),

        {'column': 'contact',
         'column_title': _(u'column_contact', u'Contact'),
         'transform': readable_ogds_author},

        {'column': 'roles',
         'column_title': _(u'column_rolelist', u'role_list'),
         'transform': role_list_helper},

        )

    def update(self):
        self.pagesize = 20
        self.pagenumber = int(self.request.get('pagenumber', 1))
        self.url = self.context.absolute_url()

        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        dossier_adpt = IDossier(self.context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append({'contact': dossier_adpt.responsible,
                        'roles': responsible_name,
                        'role_list': responsible_name,
                        })

        # XXX implement searching
        #if self.request.has_key('searchable_text'):
        #    searchable_text = self.request.get('searchable_text', None)
        #    if len(searchable_text):
        #        searchable_text = searchable_text.endswith('*')\
            #            and searchable_text[:-1] or searchable_text
            #        filter_condition = lambda p:searchable_text in p.Title()
            #        results = filter(filter_condition, results)

        if self.sort_on.startswith('header-'):
            self.sort_on = self.sort_on.split('header-')[1]
        if self.sort_on:
            sorter = lambda a, b: cmp(getattr(a, self.sort_on, ''),
                                      getattr(b, self.sort_on, ''))
            results.sort(sorter)

        if self.sort_order=='reverse':
            results.reverse()

        self.contents = results
        self.len_results = len(self.contents)

    enabled_actions = ['delete_participants',
                       'add_participant']
