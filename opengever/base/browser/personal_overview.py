from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.tabbedview.browser.tabs import Documents, Dossiers
from zope.interface import Interface


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    def get_tabs(self):
        return (
            {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
            {'id': 'mydocuments', 'icon': None, 'url': '#', 'class': None},
            )


class MyDossiers(Dossiers):
    grok.name('tabbedview_view-mydossiers')
    grok.require('zope2.View')
    grok.context(Interface)

    types = ['opengever.dossier.businesscasedossier',
             'opengever.dossier.projectdossier',]

    search_options = {'responsible': authenticated_member,}

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyDocuments(Documents):
    grok.name('tabbedview_view-mydocuments')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'Creator': authenticated_member,}


    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]
