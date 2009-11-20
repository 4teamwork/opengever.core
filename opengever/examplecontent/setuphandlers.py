from Products.CMFCore.utils import getToolByName
from random import randint
from plone.i18n.normalizer import urlnormalizer
import sys

class UserGenerator(object):
    def __init__(self, context):
        surnamesfile = context.openDataFile("surnames.csv")
        namesfile = context.openDataFile("names.csv")
        self.fileencoding = "iso-8859-1"
        self.names, self.surnames = namesfile.readlines(), surnamesfile.readlines()
        self.names_len, self.surnames_len = len(self.names), len(self.surnames)
        surnamesfile.close()
        namesfile.close()

    def getUserData(self):
        name = unicode(self.names[randint(0, self.names_len - 1)].decode(self.fileencoding).replace("\n", ""))
        surname = unicode(self.surnames[randint(0, self.surnames_len - 1)].decode(self.fileencoding).replace("\n", ""))
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
    
    if not portal.get("registraturplan"):
        portal._importObjectFromFile(context.openDataFile('registraturplan.zexp'))

	# add some default users
    regtool = portal.portal_registration
    try:
        regtool.addMember("brigitte.schmid", "demo09")
        regtool.addMember("olivier.debenat", "demo09")
        regtool.addMember("hans.muster", "demo09")
        regtool.addMember("hugo.boss", "demo09")
    except ValueError: #users already exist
        pass

    if not portal.get("arbeitsplatz"):
        portal.invokeFactory("Folder", "arbeitsplatz", title=u"Arbeitsplatz")

    arbeitsplatz = portal.get("arbeitsplatz")
    arbeitsplatz.reindexObject()

    ug = UserGenerator(context)
    for i in range(500):
        userdata = ug.getUserData()
        newid = userdata["id"]
        
        print >>sys.stdout, 'Creating user %s' % userdata["id"]
        try:
            member = regtool.addMember(userdata["id"], userdata["password"], ('Member',), None, properties={"username": userdata["id"], "email": userdata["email"]})
            member.setMemberProperties({"fullname":"%s %s" % (userdata["name"], userdata["surname"])})
        except ValueError: # memberid already exists
            pass

        