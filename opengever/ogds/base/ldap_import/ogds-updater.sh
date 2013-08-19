export ORACLE_HOME=/usr/lib/oracle/11.2/client/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

/home/zope/clients/plone01-ska-arch/bin/instance0 run /home/zope/ogds-updater/opengever/ogds/base/ldap_import/sync_ldap.py -s ska-arch

