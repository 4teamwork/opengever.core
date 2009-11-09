from Products.CMFCore.utils import getToolByName

def setup_versioning(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('opengever.document_versioning.txt') is None:
        return

    portal = context.getSite()

    # enable manual versioning for Document type
    types = [
        'opengever.document.document',
        ]
    pr = getToolByName(portal, 'portal_repository')
    for type in types:
        pr._versionable_content_types.append(type)
        pr._version_policy_mapping[type] = [
            'version_on_revert',
            ]
