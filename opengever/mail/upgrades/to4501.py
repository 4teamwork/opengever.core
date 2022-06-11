from ftw.mail.utils import ENCODED_WORD_WITHOUT_LWSP
from ftw.mail.utils import get_header
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from plone import api
from ZODB.POSException import ConflictError
import logging


log = logging.getLogger('ftw.upgrade')


def looks_incorrectly_decoded(text):
    """Determine whether a field value looks like a raw header value that
    `decode_header` failed to decode.
    """
    return bool(ENCODED_WORD_WITHOUT_LWSP.search(text))


def fix_field_value(mail, field_name, header_name):
    """Try to fix a possibly incorrectly decoded value in a field by:
    - Checking whether it looks like a raw, undecoded header
    - Checking whether it is exactly the same as the corresponding raw header
      value (which means is hasn't been edited by a user)
    - If both of the above are true, re-decode it by fetching it from the
      original message again using `get_header`
    - If the new value is different, update it on the object, reindex the
      necessary indexes, and sync the filename to the title again if needed.
    """
    updated = False
    value = getattr(mail, field_name)
    if looks_incorrectly_decoded(value) and value == mail.msg[header_name]:
        new_value = get_header(mail.msg, header_name)

        # safe_decode_headers returns UTF8, Dexterity wants unicode
        new_value = new_value.decode('utf-8')

        if value != new_value:
            log.info("Fixing '{}' for mail {} ({} -> {})".format(
                field_name, mail.absolute_url(), repr(value), repr(new_value)))
            setattr(mail, field_name, new_value)
            if field_name == 'title':
                mail.update_filename()
            updated = True

    return updated


def fix_document_author(mail):
    updated = fix_field_value(mail, 'document_author', 'From')
    if updated:
        return ['document_author',
                'SearchableText',
                'sortable_author']
    return []


def fix_title(mail):
    updated = fix_field_value(mail, 'title', 'Subject')
    if updated:
        return ['Title',
                'SearchableText',
                'sortable_title',
                'breadcrumb_titles']
    return []


class FixMailsWithIncorrectlyDecodedHeaderValues(UpgradeStep):

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')

        objects = self.catalog_unrestricted_search(
            {'portal_type': 'ftw.mail.mail'}, full_objects=True)

        info = 'Fixing mails with incorrectly decoded text'
        for mail in ProgressLogger(info, objects):
            try:
                need_reindexing = set()
                need_reindexing.update(fix_document_author(mail))
                need_reindexing.update(fix_title(mail))

                if need_reindexing:
                    catalog.reindexObject(mail, idxs=need_reindexing)
            except ConflictError:
                raise
            except Exception, e:
                log.warn("Updating object {0} failed: {1}".format(
                    mail.absolute_url(), str(e)))
