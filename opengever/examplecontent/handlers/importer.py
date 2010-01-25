import sys
import csv
import gzip
from ldif import LDIFParser, LDIFWriter
from plone.dexterity.interfaces import IDexterityContent

from ftw.directoryservice.membership import Membership

from opengever.octopus.cortex.behaviors import ICortexClient


class LDAP_Importer(object):

    def __call__(self, setup):
        self.fileencoding = 'utf8'
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.import_users()

    def active(self, setup):
        return setup.openDataFile('kanton.ldif.gz') and setup.openDataFile('mandant_order.csv') and True

    def import_users(self):
        gfile = self.openDataFile('kanton.ldif.gz')
        parser = OpenGeverLDIF(gzip.open(gfile.name), sys.stdout, self.portal, self.get_mandant_order())
        parser.parse()

    def get_mandant_order(self):
        csv_stream = self.openDataFile('mandant_order.csv')
        csv_stream.seek(0)
        dialect = csv.Sniffer().sniff(csv_stream.read(1024))
        csv_stream.seek(0)
        rows = list(csv.DictReader(csv_stream, dialect=dialect))
        return rows

class OpenGeverLDIF(LDIFParser):
    def __init__(self, input, output, portal, mandant_order):
        self.create_members = False
        LDIFParser.__init__(self, input)
        self.writer = LDIFWriter(output)
        self.portal = portal
        self.ldapIds = []
        self.mandant_order = mandant_order

        self.skip_dn = [("zgXDirektion","directorate"),("zgXSurname", "lastname"), ("givenName", "firstname"),
                        ("zgXDirektionAbk","directorate_abbr"), ("zgXAmt","department"), ("zgXAmtAbk", "department_abbr"),
                        ("mail", "email"), ("telephoneNumber", "phone_office"), ("uid", "userid")]
        
        #get all clients
        self.clients = {}
        
        for id in portal.objectIds():
            obj = portal.get(id)
            if obj.portal_type == 'ftw.directoryservice.client':
                cid = ICortexClient(obj).cid
                self.clients[cid] = obj

    def parse(self):
        LDIFParser.parse(self)
        return

    def handle(self, dn, entry):
        uid = entry.get('uid', [''])[0]

        #get the Mandant name
        filter = '%s.%s' % (entry.get('zgXDirektionAbk', [''])[0], entry.get('zgXAmtAbk', [''])[0])

        for row in self.mandant_order:
            if filter.startswith(row['filter']) or row['filter'] == '*':
                if row['mandant'] in self.clients.keys():
                    client = self.clients[row['mandant']]
                    break
        if client:
            if client.get(uid,None):
                #user exist, only sync from ldap
                contact = client.get(uid)
                if contact:
                    for l_name, c_name in self.skip_dn:
                        if contact.get(c_name)  != entry.get(l_name, [''])[0]:
                            contact.__setattr__(c_name, entry.get(l_name, [''])[0].decode('utf8'))
                self.ldapIds.append(uid)

            else:
                #user don't exist in OG, create contact in OG
                if uid != "":
                    try:
                        new_contact_id = client.invokeFactory(
                            'ftw.directoryservice.contact',
                            id=uid,
                            )
                        new_contact = client.get(new_contact_id)
                        for l_name, c_name in self.skip_dn:
                            new_contact.__setattr__(c_name, entry.get(l_name, [''])[0].decode('utf8'))


                        # #Create membership with de department
                        # if entry.get('zgXAmtAbk'):
                        #     if not entry.get('zgXAmtAbk')[0] in [o.id for o in self.folder.objectValues()]:
                        #         new_og = self.folder.invokeFactory(
                        #             'ftw.directoryservice.orgunit',
                        #             id=entry.get('zgXAmtAbk')[0],
                        #             title=entry.get('zgXAmt')[0].decode('utf8'),
                        #             )
                        #         if self.create_members:
                        #             Membership.create_membership( new_contact, self.folder.get(new_og), type="department")
                        #     else:
                        #         if self.create_members:
                        #             Membership.create_membership( new_contact, self.folder.get(entry.get('zgXAmtAbk')[0]), type="department")


                    except:
                        print entry
                else:
                    print entry
                self.ldapIds.append(uid)
