from datetime import datetime
import re

from five import grok
from zope import component
from zope.schema import getFieldsInOrder

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.dexterity.interfaces import IDexterityContent

from opengever.dossier.behaviors.dossier import IDossier
from opengever.document.document import IDocumentSchema

class CreateDocumentWithFile(grok.CodeView):
    grok.context(IDexterityContent)
    grok.name("create_document_with_file")
    grok.require("zope2.View")
    
    def render(self):
        
        title = self.request.get('title')
        uploadFile = self.request.get('file')
        filename = self.request.get('fileName')
        current_user = self.request.get('userid')
        
        
        #current_user = str(context.portal_membership.getAuthenticatedMember())
        self.context.plone_utils.changeOwnershipOf(self.context, current_user)
        
        generated_id = component.getUtility(IIDNormalizer).normalize(title)        
        id = generated_id
        counter = 1
        while 1:
            if self.context.get(id):
                id = generated_id + '-' + str(counter)
                counter += 1
            else:
                break
        
        obj = self.context.get(self.context.invokeFactory(type_name="opengever.document.document", id=id, title=title))
        
        fields = dict(getFieldsInOrder(IDocumentSchema))
        fileObj = fields['file']._type(data=uploadFile, filename=filename)
        obj.file = fileObj
        obj.document_date = datetime.now()
        
        portal = self.context.portal_url.getPortalObject()
        xpr = re.compile('href="(.*?)"')
        html = portal.externalEditLink_(obj)
        url = xpr.search(html).groups()[0]
        return url