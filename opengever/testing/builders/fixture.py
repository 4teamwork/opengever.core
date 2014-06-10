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

        self._user_args = {}
        self._hugo_boss_args = {
            'firstname': u'Hugo',
            'lastname': u'Boss',
            'userid': 'hugo.boss',
            'email': 'hugo@boss.ch',
        }
        self._org_unit_args = {
            'title': u'Client1',
            'client_id': u'client1',
        }
        self._admin_unit_args = {}

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

    def with_hugo_boss(self):
        self._with_hugo_boss = True
        return self

    def create(self):
        user = self._create_user()
        org_unit = self._create_org_unit(user)
        admin_unit = self._create_admin_unit(org_unit)
        hugo = self._create_hugo_boss()
        return [each for each in (user, org_unit, admin_unit, hugo)
                if each is not None]

    def _create_user(self):
        if not self._with_user:
            return None

        return create(Builder('ogds_user')
                      .having(**self._user_args))

    def _create_org_unit(self, user):
        if not self._with_org_unit:
            return None

        builder = (Builder('org_unit')
                   .having(**self._org_unit_args)
                   .as_current_org_unit())
        if user:
            builder = builder.with_default_groups().assign_users([user])
        return create(builder)

    def _create_admin_unit(self, org_unit):
        if not self._with_admin_unit:
            return None

        builder = Builder('admin_unit').having(
            **self._admin_unit_args).as_current_admin_unit()

        if org_unit:
            builder = builder.wrapping_org_unit(org_unit)
        return create(builder)

    def _create_hugo_boss(self):
        if not self._with_hugo_boss:
            return None

        return create(Builder('ogds_user').having(**self._hugo_boss_args))

builder_registry.register('fixture', FixtureBuilder)
