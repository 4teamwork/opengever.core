from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create


class FixtureBuilder(object):
    """Meta builder to create commont test-fixtures more easily.

    For now  this should be considered an experiment that might go away in the
    future.
    """

    def __init__(self, session):
        self.session = session
        self._with_user = False
        self._with_org_unit = False
        self._with_admin_unit = False
        self._with_hugo_boss = False

        self._user_args = {
            'firstname': u'User',
            'lastname': u'Test',
        }
        self._hugo_boss_args = {
            'firstname': u'Hugo',
            'lastname': u'Boss',
            'userid': 'hugo.boss',
            'email': 'hugo@example.com',
        }
        self._org_unit_args = {
            'title': u'Org Unit 1',
            'unit_id': u'org-unit-1',
        }
        self._admin_unit_args = {
            'title': u'Admin Unit 1',
            'unit_id': u'admin-unit-1',
            'public_url': 'http://example.com',
        }

    def with_user(self, **kwargs):
        self._with_user = True
        self._user_args.update(kwargs)
        return self

    def with_org_unit(self, **kwargs):
        self._with_org_unit = True
        self._org_unit_args.update(kwargs)
        return self

    def with_admin_unit(self, **kwargs):
        self._with_admin_unit = True
        self._admin_unit_args.update(kwargs)
        return self

    def with_all_unit_setup(self):
        self.with_user()
        self.with_org_unit()
        self.with_admin_unit()
        return self

    def with_hugo_boss(self, **kwargs):
        self._with_hugo_boss = True
        self._hugo_boss_args.update(kwargs)
        return self

    def create(self):
        user = self._create_user()
        admin_unit = self._create_admin_unit()
        org_unit = self._create_org_unit(user, admin_unit)
        hugo = self._create_hugo_boss()
        items = [each for each in (user, org_unit, admin_unit, hugo)
                 if each is not None]

        # avoid trailing comma for tuple-unpacking
        if len(items) == 1:
            return items[0]
        else:
            return items

    def _create_user(self):
        if not self._with_user:
            return None

        return create(Builder('ogds_user')
                      .having(**self._user_args))

    def _create_org_unit(self, user, admin_unit):
        if not self._with_org_unit:
            return None

        if admin_unit:
            self._org_unit_args['admin_unit'] = admin_unit
        builder = (Builder('org_unit')
                   .having(**self._org_unit_args)
                   .with_default_groups())
        if user:
            builder = (builder.as_current_org_unit()
                              .assign_users([user]))
        return create(builder)

    def _create_admin_unit(self):
        if not self._with_admin_unit:
            return None

        builder = Builder('admin_unit').having(
            **self._admin_unit_args).as_current_admin_unit()

        return create(builder)

    def _create_hugo_boss(self):
        if not self._with_hugo_boss:
            return None

        return create(Builder('ogds_user').having(**self._hugo_boss_args))


builder_registry.register('fixture', FixtureBuilder)
