import random
from plone.i18n.normalizer import urlnormalizer
import sys
from plone.dexterity.utils import createContentInContainer
from ftw.directoryservice.membership import Membership
from Products.CMFCore.utils import getToolByName

class UserGenerator(object):
    def __init__(self, context):
        surnamesfile = context.openDataFile("surnames.csv")
        namesfile = context.openDataFile("names.csv")
        self.fileencoding = "iso-8859-1"
        self.counter = 0
        self.names, self.surnames = namesfile.readlines(), surnamesfile.readlines()
        self.names_len, self.surnames_len = len(self.names), len(self.surnames)
        surnamesfile.close()
        namesfile.close()

    def getUserData(self):
        #name = unicode(self.names[randint(0, self.names_len - 1)].decode(self.fileencoding).replace("\n", ""))
        #surname = unicode(self.surnames[randint(0, self.surnames_len - 1)].decode(self.fileencoding).replace("\n", ""))
        self.counter += 1
        name = unicode(self.names[self.counter].decode(self.fileencoding).replace("\n", ""))
        surname = unicode(self.surnames[self.counter].decode(self.fileencoding).replace("\n", ""))
        userid = urlnormalizer.normalize(u"%s.%s" % (name, surname)).replace("-","").replace("..", ".")
        return {"name"    : name,
                "surname" : surname,
                "email"    : "%s@4teamwork.ch" % (userid),
                "password": "demo09",
                "id"      : userid}

def setupVarious(context):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('opengever.examplecontent_various.txt') is None:
        return
        
    portal = context.getSite()
    groupstool = portal.portal_groups

    if not portal.get("arbeitsplatz"):
        portal._importObjectFromFile(context.openDataFile('arbeitsplatz.zexp'))
        portal.get("arbeitsplatz").reindexObject()
    
    if not portal.get("ordnungssystem"):
        portal._importObjectFromFile(context.openDataFile('ordnungssystem.zexp'))

    if not portal.get("eingangskorb"):
        portal._importObjectFromFile(context.openDataFile('eingangskorb.zexp'))

    if not portal.get("aufgaben"):
        portal._importObjectFromFile(context.openDataFile('aufgaben.zexp'))

    if not portal.get("journal"):
        portal._importObjectFromFile(context.openDataFile('journal.zexp'))

    if not portal.get("kontakte"):
        portal._importObjectFromFile(context.openDataFile('kontakte.zexp'))

    if not portal.get("vorlagen"):
        portal._importObjectFromFile(context.openDataFile('vorlagen.zexp'))

    orgunitfile = context.openDataFile("orgunits.csv")
    exists = True
    # add some default orgunits
    catalog = getToolByName(portal, 'portal_catalog')
    if not catalog({
                'path':"/".join(portal.get("kontakte").getPhysicalPath()),
                'portal_type':'ftw.directoryservice.orgunit',
                'Title':orgunitfile.readline()
                }):
        exists = False
    orgunitfile.seek(0)
    if not exists:
        for orgunit in orgunitfile.readlines():
            createContentInContainer(portal.get("kontakte"), 'ftw.directoryservice.orgunit', checkConstraints=True, title=orgunit.strip())
            print >>sys.stdout, 'Creating orgunit %s' % orgunit.strip()
        
    orgunits = []
    query = {}
    query['path'] = "/".join(portal.get("kontakte").getPhysicalPath())
    query['portal_type'] = 'ftw.directoryservice.orgunit'
    for orgunit in catalog(query):
        orgunits.append(orgunit.getObject())

	# add some default users
    regtool = portal.portal_registration
    try:
        # real members
        member = regtool.addMember("GRJA", "demo09", ('Member',), None, properties={"username": "GRJA", "email": "jasmine.zehnder@zg.ch"})
        member.setMemberProperties({"fullname":"Jasmine Zehnder"})
        member = regtool.addMember("BISY", "demo09", ('Member',), None, properties={"username": "BISY", "email": "sylvia.brugger@zg.ch"})
        member.setMemberProperties({"fullname":"Sylvia Brugger"})
        member = regtool.addMember("BUEL", "demo09", ('Member',), None, properties={"username": "BUEL", "email": "gisela.vonbueren@zg.ch"})
        member.setMemberProperties({"fullname":"Gisela von Büren"})
        member = regtool.addMember("ROAH", "demo09", ('Member',), None, properties={"username": "ROAH", "email": "sarah.rojas@zg.ch"})
        member.setMemberProperties({"fullname":"Sarah Rojas-Künzle"})
        member = regtool.addMember("RAPI", "demo09", ('Member',), None, properties={"username": "RAPI", "email": "pia.raeber@zg.ch"})
        member.setMemberProperties({"fullname":"Pia Räber"})
        member = regtool.addMember("MURC", "demo09", ('Member',), None, properties={"username": "MURC", "email": "marco.mueller@zg.ch"})
        member.setMemberProperties({"fullname":"Marco Müller"})
        member = regtool.addMember("SIDD", "demo09", ('Member',), None, properties={"username": "SIDD", "email": "daniela.sidler@zg.ch"})
        member.setMemberProperties({"fullname":"Daniela Sidler"})
        member = regtool.addMember("MAST", "demo09", ('Member',), None, properties={"username": "MAST", "email": "marc.strasser@zg.ch"})
        member.setMemberProperties({"fullname":"Marc Strasser"})
        member = regtool.addMember("FUDO", "demo09", ('Member',), None, properties={"username": "FUDO", "email": "doris.furrer@zg.ch"})
        member.setMemberProperties({"fullname":"Doris Furrer"})
        member = regtool.addMember("WERO", "demo09", ('Member',), None, properties={"username": "WERO", "email": "roger.wermuth@zg.ch"})
        member.setMemberProperties({"fullname":"Roger Wermuth"})
        member = regtool.addMember("LARE", "demo09", ('Member',), None, properties={"username": "LARE", "email": "renate.landolt@zg.ch"})
        member.setMemberProperties({"fullname":"Renate Landolt"})
        member = regtool.addMember("METT", "demo09", ('Member',), None, properties={"username": "METT", "email": "matthias.meyer@zg.ch"})
        member.setMemberProperties({"fullname":"Matthias Meyer"})
        member = regtool.addMember("VIKA", "demo09", ('Member',), None, properties={"username": "VIKA", "email": "karin.bachmann@zg.ch"})
        member.setMemberProperties({"fullname":"Karin Bachmann-Villiger"})
        member = regtool.addMember("KAEL", "demo09", ('Member',), None, properties={"username": "KAEL", "email": "elisabeth.kaeppeli@zg.ch"})
        member.setMemberProperties({"fullname":"Elisabeth Käppeli"})
        member = regtool.addMember("GRIS", "demo09", ('Member',), None, properties={"username": "GRIS", "email": "isabelle.ellenberger@zg.ch"})
        member.setMemberProperties({"fullname":"Isabelle Ellenberger"})
        member = regtool.addMember("KAND", "demo09", ('Member',), None, properties={"username": "KAND", "email": "sandra.kaufmann@zg.ch"})
        member.setMemberProperties({"fullname":"Sandra Kaufmann"})
        
        # some other
        member = regtool.addMember("lesen", "demo09", ('Member',), None, properties={"username": "lesen", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"lesen"})
        member = regtool.addMember("sachbearbeiter", "demo09", ('Member',), None, properties={"username": "sachbearbeiter", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"sachbearbeiter"})
        member = regtool.addMember("vorsteher", "demo09", ('Member',), None, properties={"username": "vorsteher", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"vorsteher"})
        member = regtool.addMember("sekretariat", "demo09", ('Member',), None, properties={"username": "sekretariat", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"sekretariat"})
        member = regtool.addMember("verwalter", "demo09", ('Member',), None, properties={"username": "verwalter", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"verwalter"})
        member = regtool.addMember("admin", "demo09", ('Member',), None, properties={"username": "admin", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"admin"})
        
        member = regtool.addMember("brigitte.schmid", "demo09", ('Member',), None, properties={"username": "brigitte.schmid", "email": "brigitte.schmid@allg.zg.ch"})
        member.setMemberProperties({"fullname":"Schmid Brigitte"})
        member = regtool.addMember("olivier.debenath", "demo09", ('Member',), None, properties={"username": "olivier.debenath", "email": "olivier.debenath@allg.zg.ch"})
        member.setMemberProperties({"fullname":"Debenath Olivier"})
        member = regtool.addMember("hans.muster", "demo09", ('Member',), None, properties={"username": "hans.muster", "email": "hans.muster@4teamwork.ch"})
        member.setMemberProperties({"fullname":"Muster Hans"})
        member = regtool.addMember("hugo.boss", "demo09", ('Member',), None, properties={"username": "hugo.boss", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"Boss Hugo"})
        member = regtool.addMember("thomas.schaerli", "demo09", ('Member',), None, properties={"username": "thomas.schaerli", "email": "thomas.schaerli@gmail.com"})
        member.setMemberProperties({"fullname":"Schaerli Thomas"})

        member = regtool.addMember("admin", "demo09", ('Member', ), None, properties={"username": "admin", "email": "hugo.boss@4teamwork.ch"})
        member.setMemberProperties({"fullname":"Administrator"})
    except ValueError:
        pass
    
    # add a few default groups
    groupstool.addGroup("Sachbearbeiter")
    groupstool.getGroupById('Sachbearbeiter').addMember('sachbearbeiter')
    groupstool.addGroup("Sekretariat")
    groupstool.getGroupById('Sekretariat').addMember('sekretariat')
    groupstool.getGroupById('Sekretariat').addMember('GRJA')
    groupstool.getGroupById('Sekretariat').addMember('BISY')
    groupstool.getGroupById('Sekretariat').addMember('BUEL')
    groupstool.getGroupById('Sekretariat').addMember('ROAH')
    groupstool.getGroupById('Sekretariat').addMember('RAPI')
    groupstool.getGroupById('Sekretariat').addMember('MURC')
    groupstool.getGroupById('Sekretariat').addMember('SIDD')
    groupstool.getGroupById('Sekretariat').addMember('MAST')
    groupstool.getGroupById('Sekretariat').addMember('FUDO')
    groupstool.getGroupById('Sekretariat').addMember('WERO')
    groupstool.getGroupById('Sekretariat').addMember('LARE')
    groupstool.getGroupById('Sekretariat').addMember('METT')
    groupstool.getGroupById('Sekretariat').addMember('VIKA')
    groupstool.getGroupById('Sekretariat').addMember('KAEL')
    groupstool.getGroupById('Sekretariat').addMember('GRIS')
    groupstool.getGroupById('Sekretariat').addMember('KAND')
    groupstool.addGroup("Vorsteher")
    groupstool.getGroupById('Vorsteher').addMember('vorsteher')
    groupstool.addGroup("Verwalter")
    groupstool.getGroupById('Verwalter').addMember('verwalter')
    groupstool.getGroupById('Administrators').addMember('admin')
    
    ug = UserGenerator(context)
    group = groupstool.getGroupById('Sachbearbeiter')
    for i in range(500):
        userdata = ug.getUserData()
        newid = userdata["id"]
        if not exists:
            contact = createContentInContainer(portal.get("kontakte"), 'ftw.directoryservice.contact', checkConstraints=True, lastname=userdata["name"], firstname=userdata["surname"], userid=userdata["id"])
            # create membership
            rand = random.randrange(0,len(orgunits))
            Membership.create_membership(contact=contact,orgunit=orgunits[rand])
            print >>sys.stdout, 'Creating contact %s' % newid
            if i < 250:
                try:
                    member = regtool.addMember(userdata["id"], userdata["password"], ('Member',), None, properties={"username": userdata["id"], "email": userdata["email"]})
                    member.setMemberProperties({"fullname":"%s %s" % (userdata["surname"], userdata["name"])})
                    group.addMember(userdata["id"])
                except ValueError:
                    pass
