from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class IncreaseOGDSColumnLengths(SchemaMigration):
    """Increase lengths for several VARCHAR columns in OGDS in preparation
    for factoring out common column lengths to constants.

    (Upgrade-step for corresponding change in opengever.ogds.models)
    """

    profileid = 'opengever.ogds.base'
    upgradeid = 4301

    def migrate(self):
        self.increase_admin_unit_title_length()
        self.increase_org_unit_title_length()

        self.increase_user_firstname_length()
        self.increase_user_lastname_length()

        self.increase_user_directorate_length()
        self.increase_user_directorate_abbr_length()
        self.increase_user_department_length()
        self.increase_user_department_abbr_length()

        self.increase_user_email_length()
        self.increase_user_email2_length()

    def increase_admin_unit_title_length(self):
        # Match UNIT_TITLE_LENGTH
        self.op.alter_column('admin_units',
                             'title',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(30))

    def increase_org_unit_title_length(self):
        # Match UNIT_TITLE_LENGTH
        self.op.alter_column('org_units',
                             'title',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(30))

    def increase_user_firstname_length(self):
        # Match FIRSTNAME_LENGTH
        self.op.alter_column('users',
                             'firstname',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_user_lastname_length(self):
        # Match LASTNAME_LENGTH
        self.op.alter_column('users',
                             'lastname',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_user_directorate_length(self):
        self.op.alter_column('users',
                             'directorate',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_user_directorate_abbr_length(self):
        self.op.alter_column('users',
                             'directorate_abbr',
                             type_=String(50),
                             existing_nullable=True,
                             existing_type=String(10))

    def increase_user_department_length(self):
        self.op.alter_column('users',
                             'department',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_user_department_abbr_length(self):
        self.op.alter_column('users',
                             'department_abbr',
                             type_=String(50),
                             existing_nullable=True,
                             existing_type=String(10))

    def increase_user_email_length(self):
        # Match EMAIL_LENGTH
        self.op.alter_column('users',
                             'email',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_user_email2_length(self):
        # Match EMAIL_LENGTH
        self.op.alter_column('users',
                             'email2',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))
