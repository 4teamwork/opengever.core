# Permissions used by Poi

from Products.CMFCore import permissions as CMFCorePermissions

View = CMFCorePermissions.View
ModifyPortalContent = CMFCorePermissions.ModifyPortalContent
AccessContentsInformation = CMFCorePermissions.AccessContentsInformation

EditResponse = "Poi: Edit response"
ModifyIssueSeverity = "Poi: Modify issue severity"
ModifyIssueAssignment = "Poi: Modify issue assignment"
ModifyIssueState = "Poi: Modify issue state"
ModifyIssueTags = "Poi: Modify issue tags"
ModifyIssueWatchers = "Poi: Modify issue watchers"
ModifyIssueTargetRelease = "Poi: Modify issue target release"
UploadAttachment = "Poi: Upload attachment"

CMFCorePermissions.setDefaultRoles(EditResponse, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueSeverity, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueAssignment, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueState, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueTags, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueWatchers, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueTargetRelease, ['Manager'])
CMFCorePermissions.setDefaultRoles(UploadAttachment, ['Manager', 'Member'])

DEFAULT_ISSUE_MIME_TYPE = 'text/x-web-intelligent'
