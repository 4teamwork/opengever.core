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
        self.view.setLatexProperty('document_config', 'a4paper,11pt')
        # register logo image
        image = self.getResourceFileData('strich.png')
        self.view.addImage(uid='strich', image=image)

    def registerPackages(self):    
        self.view.registerPackage('inputenc','utf8')
        self.view.registerPackage('fontenc','T1')
        self.view.registerPackage('textcomp')
        self.view.registerPackage('arial')
        self.view.registerPackage('geometry', 'left=5cm,right=5cm,top=15cm,bottom=4cm')
        self.view.registerPackage('graphicx')

    def appendHeadCommands(self):
        self.view.appendHeaderCommand(r'\newcommand{\familydefault}{ua1}')

    def appendAboveBodyCommands(self):
        pass

    def appendBeneathBodyCommands(self):
        pass
