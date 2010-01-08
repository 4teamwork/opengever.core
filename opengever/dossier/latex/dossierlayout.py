class DossierLayout(object):
    
    def __call__(self, view, context):
        self.view = view
        self.context = context
        self.setDocumentClass()
        self.registerPackages()
        self.appendHeadCommands()
        self.appendAboveBodyCommands()
        self.appendBeneathBodyCommands()

    def getResourceFileData(self, filename, resource='opengever.dossier.latex.resource'):
        fiveFile = self.context.restrictedTraverse('++resource++%s/%s' % (resource, filename))
        path = fiveFile.context.path
        fileData = open(path).read()
        return fileData

    def setDocumentClass(self):
        self.view.setLatexProperty('document_class', 'article')
        self.view.setLatexProperty('document_config', 'a4paper,10pt,parskip=half')
        # register logo image
        image = self.getResourceFileData('logo_sw.pdf')
        self.view.addImage(uid='logo_sw', image=image)

    def registerPackages(self):
        self.view.registerPackage('graphicx')
        self.view.registerPackage('helvet')
        self.view.registerPackage('wrapfig')
        self.view.registerPackage('longtable')
        self.view.registerPackage('titlesec', 'compact')
        self.view.registerPackage('geometry', 'left=35mm,right=10mm,top=55mm,bottom=30.5mm')
        self.view.registerPackage('fancyhdr')
        self.view.registerPackage('paralist', 'neveradjust')
        self.view.registerPackage('textpos', 'absolute, overlay')
        self.view.registerPackage('ifthen')

    def appendHeadCommands(self):
        member = self.getOwnerMember()
        self.view.appendHeaderCommand(r'\newcommand{\Autor}{%s}' % r'')
        self.view.appendHeaderCommand(r'\newcommand{\Titel}{%s}' %
            self.context.pretty_title_or_id().encode('utf8'))
        self.view.appendHeaderCommand(r'\newcommand{\CreatorDirektion}{%s}' %
                        self.view.convert(member and member.getProperty('direktion', '-') or '-'))
        self.view.appendHeaderCommand(r'\newcommand{\CreatorAmt}{%s}' %
                        self.view.convert(member and member.getProperty('amt', '-') or '-'))
        # and embed local head_commands.tex (overwrites the bibliothek-one partially)
        head_commands = self.getResourceFileData('head_commands.tex')
        self.view.appendHeaderCommand(head_commands)

    def appendAboveBodyCommands(self):
        self.view.appendToProperty('latex_above_body', r'\thispagestyle{myheadings}')

    def appendBeneathBodyCommands(self):
        pass
        #self.view.appendToProperty('latex_beneath_body', r'')

    def getOwnerMember(self):
        creator_id = self.context.Creator()
        return self.context.portal_membership.getMemberById(creator_id)
