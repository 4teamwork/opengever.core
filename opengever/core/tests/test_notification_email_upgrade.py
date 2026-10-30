from alembic.migration import MigrationContext
from alembic.operations import Operations
from importlib import import_module
from mock import Mock
from opengever.base.interfaces import IOGMailSettings
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.registry.exportimport.handler import RegistryImporter
from plone.registry.interfaces import IRegistry
from sqlalchemy import create_engine
from sqlalchemy import inspect
from zope.component import getUtility
import os
import unittest


COLUMN_UPGRADE = 'opengever.core.upgrades.20261030100000_add_notification_email_column.upgrade'
FLAG_UPGRADE = 'opengever.core.upgrades.20261030100100_add_alternative_notification_email_flag.upgrade'


class TestNotificationEmailColumnUpgrade(unittest.TestCase):

    def test_additive_migration_preserves_existing_settings(self):
        engine = create_engine('sqlite://')
        with engine.connect() as connection:
            connection.execute('CREATE TABLE user_settings '
                               '(userid VARCHAR(255) PRIMARY KEY, '
                               'notify_own_actions BOOLEAN NOT NULL)')
            connection.execute("INSERT INTO user_settings VALUES ('owner', 1)")
            migration_class = import_module(COLUMN_UPGRADE).AddNotificationEmailColumn
            migration = object.__new__(migration_class)
            migration.op = Operations(MigrationContext.configure(connection))
            migration.migrate()
            columns = {col['name']: col for col in inspect(connection).get_columns('user_settings')}
            self.assertTrue(columns['notification_email']['nullable'])
            self.assertEqual(255, columns['notification_email']['type'].length)
            self.assertEqual(('owner', 1, None), tuple(connection.execute(
                'SELECT userid, notify_own_actions, notification_email FROM user_settings').first()))
            connection.execute("UPDATE user_settings SET notification_email = 'private@example.org'")
            self.assertEqual('private@example.org', connection.execute(
                'SELECT notification_email FROM user_settings').scalar())
        engine.dispose()

    def test_fresh_schema_includes_nullable_bounded_column(self):
        column = UserSettings.__table__.columns['notification_email']
        self.assertTrue(column.nullable)
        self.assertEqual(255, column.type.length)
        self.assertIsNone(column.default)


class TestNotificationEmailRegistryUpgrade(IntegrationTestCase):

    def test_adds_default_off_flag_without_resetting_sender_configuration(self):
        self.login(self.manager)
        registry = getUtility(IRegistry)
        key = 'opengever.base.interfaces.IOGMailSettings.alternative_notification_email_enabled'
        del registry.records[key]
        api.portal.set_registry_record('send_with_actor_from_address', True, IOGMailSettings)
        environ = Mock()
        environ.shouldPurge.return_value = False
        upgrade_module = import_module(FLAG_UPGRADE)
        with open(os.path.join(os.path.dirname(upgrade_module.__file__), 'registry.xml')) as stream:
            RegistryImporter(registry, environ).importDocument(stream.read())
        self.assertFalse(api.portal.get_registry_record(
            'alternative_notification_email_enabled', interface=IOGMailSettings))
        self.assertTrue(api.portal.get_registry_record(
            'send_with_actor_from_address', interface=IOGMailSettings))
