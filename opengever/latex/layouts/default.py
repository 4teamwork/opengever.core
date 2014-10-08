from five import grok
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.layout.customizable import CustomizableLayout
from opengever.latex.interfaces import ILaTeXSettings
from opengever.ogds.base.utils import get_current_admin_unit
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.interface import Interface


class DefaultLayout(CustomizableLayout, grok.MultiAdapter):
    """Opengever default layout.
    """
    grok.adapts(Interface, Interface, IBuilder)
    grok.provides(ILaTeXLayout)

    template_directories = ['resources']
    template_name = 'default_layout.tex'

    def __init__(self, context, request, builder):
        super(DefaultLayout, self).__init__(context, request, builder)
        self.show_contact = False
        self.show_logo = False
        self.show_organisation = False

    def before_render_hook(self):
        self.use_package('inputenc', options='utf8', append_options=False)
        self.use_package('ae,aecompl')
        self.use_package('babel', 'ngerman', append_options=False)
        self.use_package('fancyhdr')

        self.use_package('geometry', 'left=35mm')
        self.use_package('geometry', 'right=10mm')
        self.use_package('geometry', 'top=55mm')
        self.use_package('geometry', 'bottom=10.5mm')

        self.use_package('graphicx')
        self.use_package('lastpage')
        self.use_package('paralist', 'neveradjust', append_options=False)
        self.use_package('textcomp')

        self.use_package('textpos', 'absolute')
        self.use_package('textpos', 'overlay')
        self.use_package('titlesec', 'compact')
        self.use_package('wrapfig')
        self.use_package('array,supertabular')
        self.use_package('setspace')

        if self.show_logo:
            self.add_raw_template_file('gever_logo.jpeg')

    def get_render_arguments(self):
        owner = self.get_owner()

        owner_phone = '&nbsp;'
        if owner:
            owner_phone = owner.getProperty('phone_number', '&nbsp;')

        convert = self.get_converter().convert
        return {
            'client_title': convert(self.get_current_admin_unit_label()),
            'member_phone': convert(owner_phone),
            'show_contact': self.show_contact,
            'show_logo': self.show_logo,
            'show_organisation': self.show_organisation,
            'location': convert(self.get_location())}

    def get_current_admin_unit_label(self):
        return get_current_admin_unit().label()

    def get_location(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ILaTeXSettings).location

    def get_owner(self):
        mtool = getToolByName(self.context, 'portal_membership')
        creator_id = self.context.Creator()
        return mtool.getMemberById(creator_id)
