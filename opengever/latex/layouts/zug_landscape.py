from zug_default import ZugDefaultLayout


class ZugLandscapeLayout(ZugDefaultLayout):


    def setDocumentClass(self):
        """ Sets the document class and adds the logo-image
        """
        self.view.setLatexProperty('document_class', 'article')
        self.view.setLatexProperty('document_config', 'landscape,a4paper,10pt')
        # register logo image
        image = self.getResourceFileData(
            'logo_sw.pdf')
        self.view.addImage(uid='logo_sw', image=image)

    def appendAboveBodyCommands(self):
        """ Appends above body commands
        """
        self.view.appendToProperty(
            'latex_above_body',
            self.getResourceFileData('zuglandscape_above_body.tex'))
