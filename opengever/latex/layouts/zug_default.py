from opengever.ogds.base.utils import get_current_client


class ZugDefaultLayout(object):
    """Default LaTeX layout for zug.
    """

    customconverters = []

    def __init__(self, show_logo=True, show_organisation=False,
                 show_contact=True):
        self.show_logo = show_logo
        self.show_contact = show_contact
        self.show_organisation = show_organisation

    def __call__(self, view, context):
        self.view = view
        self.context = context
        self.setDocumentClass()
        self.registerPackages()
        self.appendHeadCommands()
        self.appendAboveBodyCommands()
        self.appendBeneathBodyCommands()
        self.configureconverter()

    def getResourceFileData(self, filename,
                            resource='opengever.latex.layouts.resources'):
        """ Returns a resource-file
        """
        fiveFile = self.context.restrictedTraverse('++resource++%s/%s' %
                                                   (resource, filename))
        path = fiveFile.context.path
        fileData = open(path).read()
        return fileData

    def setDocumentClass(self):
        """ Sets the document class and adds the logo-image
        """
        self.view.setLatexProperty('document_class', 'article')
        self.view.setLatexProperty('document_config', 'a4paper,10pt')
        # register logo image
        image = self.getResourceFileData(
            'logo_sw.pdf')
        self.view.addImage(uid='logo_sw', image=image)

    def registerPackages(self):
        """ Registers the packages used for this layout.
        Content-specific packages may be added by the content-converter or
        a HTML-subconverter
        """
        self.view.registerPackage('ae,aecompl')
        self.view.registerPackage('babel', 'ngerman')
        self.view.registerPackage('fancyhdr')
        self.view.registerPackage(
            'geometry', 'left=35mm,right=10mm,top=55mm,bottom=10.5mm')
        self.view.registerPackage('graphicx')
        self.view.registerPackage('ifthen')
        self.view.registerPackage('lastpage')
        self.view.registerPackage('paralist', 'neveradjust')
        self.view.registerPackage('textcomp')
        self.view.registerPackage('textpos', 'absolute, overlay')
        self.view.registerPackage('titlesec', 'compact')
        self.view.registerPackage('wrapfig')
        self.view.registerPackage('array,supertabular')
        self.view.registerPackage('setspace')

    def appendHeadCommands(self):
        """ Appends static head commands
        and dynamic head commands such as renewcommand for Title
        """
        # static head commands
        self.view.appendHeaderCommand(
            self.getResourceFileData('zugdefault_head.tex'))
        # print dynamic header commands
        self.view.appendHeaderCommand('%% %s' % ('-' * 65))
        self.view.appendHeaderCommand('% DYNAMIC HEADER COMMANDS')
        self.view.appendHeaderCommand('%% %s' % ('-' * 65))
        # renewcommands:
        vars = {
            'Titel': self.context.Title() or '',
            }
        member = self.getOwnerMember()
        client = get_current_client()
        vars['CreatorDirektion'] = 'Direktionsname?'
        vars['CreatorAmt'] = client.title

        if member and member.getProperty('email', False):
            vars['CreatorEmail'] = member.getProperty('email')
        if member and member.getProperty('phone_number', '&nbsp;'):
            vars['CreatorPhone'] = self.view.convert(
                member.getProperty('phone_number', '&nbsp;'))

        for key, value in vars.items():
            self.view.appendHeaderCommand(r'\renewcommand{\%s}{%s}' % (
                    key, self.view.convert(value)))
        # booleans
        bools = {
            'logo': self.show_logo,
            'organisation': self.show_organisation,
            'contact': self.show_contact,
            }
        for key, value in bools.items():
            self.view.appendHeaderCommand(r'\setboolean{%s}{%s}' % (
                    key, value and 'true' or 'false'))

    def appendAboveBodyCommands(self):
        """ Appends above body commands
        """
        self.view.appendToProperty(
            'latex_above_body',
            self.getResourceFileData('zugdefault_above_body.tex'))

    def appendBeneathBodyCommands(self):
        """ Appends beneath body commands
        """
        pass

    def getOwnerMember(self):
        """ Returns the member-object of the creator of the context-object
        """
        creator_id = self.context.Creator()
        return self.context.portal_membership.getMemberById(creator_id)

    def configureconverter(self):
        converter = self.view.html2latex_converter
        for cc in self.customconverters:
            converter._insertCustomPattern(**converter._getMappingByConverter(cc))
