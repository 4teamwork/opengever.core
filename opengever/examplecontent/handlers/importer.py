import sys
import gzip
from ldif import LDIFParser, LDIFWriter
from five import grok
from plone.dexterity.interfaces import IDexterityContent

from ftw.directoryservice.membership import Membership


class LDAP_Importer(object):
    
    def __call__(self, setup):
        self.fileencoding = 'utf8'
        self.setup = setup
        self.portal = self.setup.getSite()
        self.gds = self.portal.get('gds', None)
        self.openDataFile = self.setup.openDataFile
        self.import_users()

    def active(self, setup):
        return setup.openDataFile('kanton.ldif.gz') and True

    def import_users(self):
        import pdb; pdb.set_trace( )
        gfile = self.openDataFile('kanton.ldif.gz')
        parser = OpenGeverLDIF(gzip.open(gfile.name), sys.stdout, self.gds)
        parser.parse()


class OpenGeverLDIF(LDIFParser):
    def __init__(self, input, output, folder):
        LDIFParser.__init__(self, input)
        self.writer = LDIFWriter(output)
        self.folder = folder
        self.ldapIds = []

        self.skip_dn = [("zgXDirektion","directorate"),("zgXSurname", "lastname"), ("givenName", "firstname"), 
        ("zgXDirektionAbk","directorate_abbr"), ("zgXAmt","department"), ("zgXAmtAbk", "department_abbr"),
        ("mail", "email"), ("telephoneNumber", "phone_office"), ("uid", "userid")]
    
    def parse(self):
        LDIFParser.parse(self)
        return

    def handle(self, dn, entry):
        uid = entry.get('uid', [''])[0]
        
        if self.folder.get(uid,None):
            #user exist, only sync from ldap
            contact = self.folder.get(uid)
            if contact:
                for l_name, c_name in self.skip_dn:
                    if contact.get(c_name)  != entry.get(l_name, [''])[0]:
                        contact.__setattr__(c_name, entry.get(l_name, [''])[0].decode('utf8'))
            self.ldapIds.append(uid)
            
        else:
            #user don't exist in OG, create contact in OG
            if uid != "":
                try:
                    new_contact_id = self.folder.invokeFactory(
                        'ftw.directoryservice.contact',
                        id=uid,
                    )
                    new_contact = self.folder.get(new_contact_id)
                    for l_name, c_name in self.skip_dn:
                        new_contact.__setattr__(c_name, entry.get(l_name, [''])[0].decode('utf8'))

                    #Create membership with de department
                    if entry.get('zgXAmtAbk'):
                        if not entry.get('zgXAmtAbk')[0] in [o.id for o in self.folder.objectValues()]:
                            new_og = self.folder.invokeFactory(
                                'ftw.directoryservice.orgunit',
                                id=entry.get('zgXAmtAbk')[0],
                                title=entry.get('zgXAmt')[0].decode('utf8'),
                            )
                            Membership.create_membership( new_contact, self.folder.get(new_og), type="department")
                        else:
                            Membership.create_membership( new_contact, self.folder.get(entry.get('zgXAmtAbk')[0]), type="department")
                except:
                    print entry
                
            else:
                print entry
            self.ldapIds.append(uid)
