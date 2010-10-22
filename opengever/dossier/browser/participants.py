import base64

from five import grok
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.helper import readable_ogds_author
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier import _


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
        (_(u'column_contact', u'Contact'), 'contact', readable_ogds_author),
        (_(u'column_rolelist',u'role_list'), 'roles', ))

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
