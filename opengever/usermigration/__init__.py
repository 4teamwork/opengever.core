from ftw.usermigration.browser import migration
from opengever.usermigration.localroles import migrate_localroles


migration.BUILTIN_MIGRATIONS['localroles'] = migrate_localroles
