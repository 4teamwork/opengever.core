from App.config import getConfiguration
from argparse import ArgumentTypeError
from ftw.tokenauth.service_keys.browser.issue import create_json_keyfile
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from plone import api
from random import SystemRandom
import argparse
import logging
import os
import string
import sys
import transaction


log = logging.getLogger("opengever.setup.serviceuser")
log.setLevel(logging.INFO)


def make_random_password():
    random = SystemRandom()
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for i in range(32))


def new_user(username):
    username = username.strip()
    acl_users = api.portal.get_tool("acl_users")
    user = acl_users.getUser(username)
    if user is not None:
        raise ArgumentTypeError(u"User {} already exists.".format(username))
    return username


def parse_args(argv):
    """Parse arguments and insert defaults."""

    # Discard the first two arguments, because they're not "actual" arguments
    # but cruft that we get because of the way bin/instance [zopectl_cmd]
    # scripts work.
    if sys.argv[0] != 'create_service_user':
        argv = argv[2:]

    acl_users = api.portal.get_tool("acl_users")
    allowed_roles = list(acl_users.portal_role_manager.listRoleIds())

    parser = argparse.ArgumentParser(description="Create a service user.")
    parser.add_argument(
        "username", help="Username of the service user.", type=new_user
    )
    parser.add_argument(
        "--roles",
        nargs="+",
        default=[],
        required=False,
        choices=allowed_roles,
        help="The roles of the service user. Will always inlcude the "
        "`ServiceKeyUser` role.",
    )
    parser.add_argument(
        "--service-key-title",
        default=None,
        required=False,
        help="Title for the service key. Uses <username> by default.",
    )

    parsed_args = parser.parse_args(argv)

    # service users must always have the `ServiceKeyUser` role.
    roles = set(parsed_args.roles)
    roles.add("ServiceKeyUser")
    parsed_args.roles = sorted(roles)

    if not parsed_args.service_key_title:
        parsed_args.service_key_title = parsed_args.username

    return parsed_args


def add_user(parsed_args):
    """Create the user in `acl_users`."""

    acl_users = api.portal.get_tool("acl_users")
    username = parsed_args.username
    roles = parsed_args.roles

    # we don't use a domain
    domains = []
    # We don't want to directly login with this user but just via its token.
    password = make_random_password()

    log.info(
        u"Creating user {} with roles {}.".format(username, ", ".join(roles))
    )
    user = acl_users._doAddUser(username, password, roles, domains)
    if not user:
        log.error(u"Could not create user {}".format(username))
        sys.exit(1)

    log.info(u"User {} has been created.".format(user.getId()))
    return user


def setup_token_auth(user, parsed_args):
    """Set up token auth for the user and write its key to the file system."""

    acl_users = api.portal.get_tool("acl_users")
    token_auth = acl_users["token_auth"]
    user_id = user.getId()
    service_key_title = parsed_args.service_key_title

    private_key, service_key = token_auth.issue_keypair(
        user_id, service_key_title, ip_range=None
    )
    json_keyfile = create_json_keyfile(private_key, service_key)

    cfg = getConfiguration()
    outdir = cfg.clienthome
    filename = u"{}.json".format(user_id)
    filepath = os.path.join(outdir, filename)
    log.info(u"Writing key to {}".format(filepath))
    with open(filepath, "w") as fp:
        fp.write(json_keyfile)


def create_service_user_zopectl_handler(app, args):
    """Handler for the 'bin/instance create_service_user' zopectl command."""
    setup_logging()
    setup_plone(get_first_plone_site(app))

    parsed_args = parse_args(args)
    user = add_user(parsed_args)
    setup_token_auth(user, parsed_args)
    transaction.commit()


def setup_logging():
    """Set Zope's default StreamHandler's level to INFO (default is WARNING)
    to make sure output gets logged on console.
    """
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
