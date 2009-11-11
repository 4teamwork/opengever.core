from Products.CMFCore.utils import getToolByName

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