from App.config import getConfiguration
from ftw.builder import Builder
from ftw.builder import create
from ftw.tokenauth.pas.storage import CredentialStorage
from opengever.setup.serviceuser import create_service_user_zopectl_handler
from opengever.setup.serviceuser import parse_args
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import CapturingLogHandler
from plone import api
import json
import logging
import os


class TestCreateServiceUserZopectlHandler(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestCreateServiceUserZopectlHandler, self).setUp()
        self.args = ["-c", "ignored"]

        self.logger = logging.getLogger("opengever.setup.serviceuser")
        self.logger.setLevel(logging.INFO)
        self.log_handler = CapturingLogHandler()
        self.logger.addHandler(self.log_handler)

    def test_parse_args_default_arguments(self):
        self.args.append("some_user")
        parsed_args = parse_args(self.args)

        self.assertEqual(["ServiceKeyUser"], parsed_args.roles)
        self.assertEqual("some_user", parsed_args.service_key_title)

    def test_create_service_user(self):
        username = "default"
        self.args.extend([username, "--service-key-title", "some app"])
        create_service_user_zopectl_handler(self.app, self.args)

        cfg = getConfiguration()
        outdir = cfg.clienthome
        filename = u"{}.json".format(username)
        filepath = os.path.join(outdir, filename)

        self.assertEqual(
            [
                u"Creating user default with roles ServiceKeyUser.",
                u"User default has been created.",
                u"Writing key to {}".format(filepath),
            ],
            self.log_handler.msgs,
        )

        pas = api.portal.get_tool("acl_users")
        user = pas.getUser(username)
        self.assertIsNotNone(user)

        role_manager = pas.portal_role_manager
        self.assertItemsEqual(
            ["ServiceKeyUser"], role_manager.getRolesForPrincipal(user)
        )

        with open(filepath) as fp:
            json_data = json.load(fp)
        self.assertIn("private_key", json_data)
        self.assertEqual(username, json_data["user_id"])

        storage = CredentialStorage(pas["token_auth"])
        keys = storage.list_service_keys(username)
        self.assertEqual(1, len(keys))
        self.assertDictContainsSubset(
            {
                "user_id": "default",
                "title": "some app",
                "ip_range": None,
            },
            keys[0],
        )

    def test_create_service_user_with_additional_roles(self):
        username = "moreRoles"
        self.args.extend([username, "--roles", "Member", "Impersonator"])
        create_service_user_zopectl_handler(self.app, self.args)

        self.assertEqual(
            u"Creating user moreRoles with roles Impersonator, Member, "
            u"ServiceKeyUser.",
            self.log_handler.msgs[0],
        )

        pas = api.portal.get_tool("acl_users")
        user = pas.getUser(username)
        self.assertIsNotNone(user)

        role_manager = pas.portal_role_manager
        self.assertItemsEqual(
            ["Impersonator", "Member", "ServiceKeyUser"],
            role_manager.getRolesForPrincipal(user),
        )

    def test_prevents_adding_existing_user(self):
        create(
            Builder("user")
            .having(firstname="Hugo", lastname="Boss")
            .with_userid("hugo.boss")
        )

        username = "hugo.boss"
        self.args.append(username)

        # parse_args will exit in case of invalid arguments
        # we refrain from lookint at stdout/stderr too much and just
        # test this in a very generic way
        with self.assertRaises(SystemExit):
            create_service_user_zopectl_handler(self.app, self.args)

    def test_prevents_using_invalid_roles(self):
        username = "foo"
        self.args.extend([username, "--roles", "invalid"])

        # parse_args will exit in case of invalid arguments
        # we refrain from lookint at stdout/stderr too much and just
        # test this in a very generic way
        with self.assertRaises(SystemExit):
            create_service_user_zopectl_handler(self.app, self.args)
