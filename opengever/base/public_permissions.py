# This maps the plone and gever permissions to simpler permisison names.
# This is used to decouple internal permissions from permission names used
# from the outside, for example by external applications or the API.

PUBLIC_PERMISSIONS_MAPPING = {
    'edit': 'Modify portal content',
    'trash': 'opengever.trash: Trash content',
    'untrash': 'opengever.trash: Untrash content',
    'manage-security': 'Sharing page: Delegate roles',
    'add:opengever.dossier.businesscasedossier': 'opengever.dossier: Add businesscasedossier',
    'add:opengever.document.document': 'opengever.document: Add document',
    'add:ftw.mail.mail': 'ftw.mail: Add Mail',
    'add:opengever.contact.contact': 'opengever.contact: Add contact',
    'add:opengever.repository.repositoryfolder': 'opengever.repository: Add repositoryfolder',
    'add:opengever.repository.repositoryroot': 'opengever.repository: Add repositoryroot',
    }
