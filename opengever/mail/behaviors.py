from plone.directives import form

class IMailInAddress(form.Schema):
    
    def get_email_address(self):
        """ generates an email adress for a dossier
        """