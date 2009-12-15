from plone.i18n.normalizer import urlnormalizer
import sys

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

	# add some default users
    regtool = portal.portal_registration
    try:

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

    except ValueError: #users already exist
        pass

    if not portal.get("arbeitsplatz"):
        portal.invokeFactory("Folder", "arbeitsplatz", title=u"Arbeitsplatz")

    arbeitsplatz = portal.get("arbeitsplatz")
    arbeitsplatz.reindexObject()
    
    # add a few default groups
    groupstool.addGroup("Sachbearbeiter")
    groupstool.getGroupById('Sachbearbeiter').addMember('sachbearbeiter')
    groupstool.addGroup("Sekretariat")
    groupstool.getGroupById('Sekretariat').addMember('sekretariat')
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
        
        print >>sys.stdout, 'Creating user %s' % userdata["id"]
        try:
            member = regtool.addMember(userdata["id"], userdata["password"], ('Member',), None, properties={"username": userdata["id"], "email": userdata["email"]})
            member.setMemberProperties({"fullname":"%s %s" % (userdata["surname"], userdata["name"])})
            group.addMember(userdata["id"])
        except ValueError: # memberid already exists
            pass
    
        
