"""
Helper module to read and configure LDAP credentials from a JSON file.

`configure_ldap_credentials()` will iterate over all LDAP plugins on the site
and look for a file ~/.opengever/ldap/{hostname}.json in the following format:

{
  "<plugin_id_1>":{
    "password":"verysecret",
    "user":"cn=Admin,ou=Foo,dc=example,dc=org"
  },
  "<plugin_id_2>":{
    "password":"foo",
    "user":"bar"
  }
}

<plugin_id> is the ID of the LDAPMultiPlugin (not the LDAPUserFolder inside
it!), as defined in ldap_plugin.xml with <ldapplugin id="..." />.

It then configures username and password on the respective LDAP plugin with
the credentials from that file - so the ldap_plugin.xml needs to contain
*everything* necessary to configure the plugin, excepct the `_binduid` and 
`_bindpwd`.
"""

from os.path import join as pjoin
from Products.CMFCore.utils import getToolByName
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
import json
import logging
import os


logger = logging.getLogger('opengever.setup')


def get_credentials_file_path(hostname):
    dotdir = os.path.expanduser(pjoin('~', '.opengever'))
    creds_path = pjoin(dotdir, 'ldap', '%s.json' % hostname)
    return creds_path


def get_ldap_credentials(hostname):
    creds_path = get_credentials_file_path(hostname)
    if not os.path.exists(creds_path):
        return None

    creds_file = open(creds_path, 'r')
    credentials = json.loads(creds_file.read())
    return credentials


def configure_ldap_credentials(context):
    site = getToolByName(context, 'portal_url').getPortalObject()
    ldap_plugins = [obj for obj in site.acl_users.objectValues()
                        if ILDAPMultiPlugin.providedBy(obj)]
    for ldap_plugin in ldap_plugins:
        ldap_uf = ldap_plugin.acl_users
        server = ldap_uf.getServers()[0]
        hostname = server['host']

        credentials = get_ldap_credentials(hostname)
        if credentials:
            binduid = credentials[ldap_plugin.id]['user'].encode('utf-8')
            bindpwd = credentials[ldap_plugin.id]['password'].encode('utf-8')

            # Update username and password on the LDAPUserFolder
            ldap_uf._binduid = binduid
            ldap_uf._bindpwd = bindpwd
            ldap_uf.binduid_usage = 1

            # Update username and password on the currently active LDAP connection
            ldap_uf._delegate.binduid_usage = 1
            ldap_uf._delegate.bind_dn = binduid
            ldap_uf._delegate.bind_pwd = bindpwd

            logger.info("Sucessfully configured LDAP credentials for '%s' (%s)." % (
                ldap_plugin.id,
                hostname))
        else:
            creds_file_path = get_credentials_file_path(hostname)
            logger.warn("No LDAP credentials file found for '%s' (%s)! "
                        "Make sure '%s' exists and has the proper format." % (
                        ldap_plugin.id, hostname, creds_file_path))
