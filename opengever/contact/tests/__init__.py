from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import create_session
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment


def set_roles(obj, principal, roles):
    RoleAssignmentManager(obj).add_or_update_assignment(
        SharingRoleAssignment(principal, roles))


def create_contacts(self):
    self.contactfolder = create(
        Builder('contactfolder')
        .having(
            id='kontakte',
            title_de=u'Kontakte',
            title_en=u'Contacts',
            title_fr=u'Contacts',
        )
    )

    set_roles(self.contactfolder, 'fa_users', ['Reader'])

    set_roles(self.contactfolder, 'fa_users', ['Reader', 'Contributor', 'Editor'])

    self.contactfolder.reindexObjectSecurity()

    self.hanspeter_duerr = create(
        Builder('contact')
        .within(self.contactfolder)
        .having(
            firstname=u'Hanspeter',
            lastname='D\xc3\xbcrr'.decode('utf-8'),
        )
    )

    self.franz_meier = create(
        Builder('contact')
        .within(self.contactfolder)
        .having(
            firstname=u'Franz',
            lastname=u'Meier',
            email=u'meier.f@example.com',
        )
    )
    create_session().flush()
