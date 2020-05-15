from plone.i18n.normalizer.base import CHAR as base_cache
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
import re
import string
import unicodedata

# We share the cache with the plone basenormalizer as there seems
# to be little reason to cache the unicode tables twice.
unicode_cache = base_cache

# On OpenBSD string.whitespace has a non-standard implementation
# See http://dev.plone.org/plone/ticket/4704 for details
whitespace = ''.join([c for c in string.whitespace if ord(c) < 128])
allowed_characters = string.ascii_letters + string.digits + string.punctuation + whitespace


def unidecode(string):
    """This function is taken and adapted from the unidecode module.
    It replaces unicode characters with their closest ASCII counterpart
    or with a whitespace.
    """
    retval = []

    for char in string:
        codepoint = ord(char)

        if codepoint < 0x80:  # Basic ASCII
            retval.append(str(char))
            continue

        if codepoint > 0xeffff:
            retval.append(' ')
            continue  # Characters in Private Use Area and above are ignored

        section = codepoint >> 8   # Chop off the last two hex digits
        position = codepoint % 256  # Last two hex digits
        try:
            table = unicode_cache[section]
        except KeyError:
            try:
                mod = __import__('unidecode.x%02x' % (section), [], [], ['data'])
            except ImportError:
                unicode_cache[section] = None
                retval.append(' ')
                continue   # No match: ignore this character and carry on.

            unicode_cache[section] = table = mod.data

        if table and len(table) > position:
            retval.append(table[position])

        elif unicodedata.decomposition(char):
            normalized = unicodedata.normalize('NFKD', char).strip()
            normalized = ''.join([c for c in normalized if c in allowed_characters])
            retval.append(normalized or ' ')

        else:
            retval.append(' ')

    return ''.join(retval)


class GeverBaseStringNormalizer(object):
    """This normalizer is meant as a flexible baseclass for
    string normalizers in opengever. Its normalize method will:
    * make the string NFKC encoded unicode
    * apply the character mapping defined in self.unicode_mapping
    * transliterate unicode characters, inserting spaces for characters
      that cannot be transliterated
    * apply regular expression substitutions defined in self.regex_substitution_list
    * strip leading spaces
    * crop the resulting string to self.max_length (if None, do not crop)
    * strip trailing spaces
    """

    def __init__(self):
        self.unicode_mapping = {}
        self.regex_substitution_list = tuple()
        self.max_length = 50

    def normalize(self, text):
        text = safe_unicode(text)
        text = unicodedata.normalize('NFKC', text)
        text = self.map_unicode(text)
        text = unidecode(text)
        text = self.apply_regex_substitutions(text)
        text = text.lstrip()
        text = self.crop_length(text)
        text = text.rstrip()
        return safe_unicode(text)

    def map_unicode(self, text):
        """
        This method is used to replace special characters found in a mapping.
        """
        res = u''
        for ch in text:
            ordinal = ord(ch)
            if ordinal in self.unicode_mapping:
                res += self.unicode_mapping.get(ordinal)
            else:
                res += ch
        return res

    def apply_regex_substitutions(self, text):
        for regex, substitution_string in self.regex_substitution_list:
            text = regex.sub(substitution_string, text)
        return text

    def crop_length(self, text):
        if self.max_length is None:
            return text
        return text[:self.max_length]


class GeverFileNameNormalizer(GeverBaseStringNormalizer):
    """This normalizer is used to generate normalized filenames
    typically from the title of an object, making the filename safe
    but as close as possible to the original title.
    Specifically it will:
    * Use a custom map for transliterating German characters as
      well as map & to +
    * Transliterate other unicode characters using unidecode
    * Only keep safe characters (letters, digits, whitespace and _.,=()+-)
    * Replace all other characters with whitespace
    * Replace consecutive spaces with a single space
    * Truncate the length of the filename to 100 characters, not including the
      extension (which which is limited to 5 characters with the current regex
      used to determine it), so 105 total.

    In addition to the above, the filename extension normalization includes:
    * make the string lowercase
    * map jpeg to jpg and tiff to tif
    """
    implements(IFileNameNormalizer)

    def __init__(self):
        super(GeverFileNameNormalizer, self).__init__()

        # This maximal length should not be changed without also adapting
        # the favorite model (opengever/base/favorite.py)
        self.max_length = 100

        self.unicode_mapping = {196: u'Ae', 198: u'Ae', 214: u'Oe', 220: u'Ue',
                                228: u'ae', 230: u'ae', 246: u'oe', 252: u'ue',
                                223: u'ss', 224: u'a', 339: u'oe', 38: u'+'}

        self.extension_mapping = {u'tiff': u'tif', u'jpeg': u'jpg'}

        self.allowed_characters = string.ascii_letters + string.digits + ' _.,=()+-'

        forbidden_chars_regex = re.compile(r"[^{}]+".format(self.allowed_characters))
        multiple_spaces_regex = re.compile(r" +")

        self.regex_substitution_list = ((forbidden_chars_regex, ' '),
                                        (multiple_spaces_regex, ' '))

        # changing this regex and allowing longer extensions will have an
        # influence on the total filename length
        self.filename_extension_regex = re.compile(r"^(.+)\.(\w{,4})$")

    def split_filename_extension(self, filename):
        match = self.filename_extension_regex.search(filename)
        if match is not None:
            filename = match.groups()[0]
            extension = match.groups()[1]
            return filename, extension
        return filename, ''

    def normalize_name(self, text):
        text = super(GeverFileNameNormalizer, self).normalize(text)
        text = self.crop_length(text)
        return text

    def normalize_extension(self, extension):
        extension = self.extension_mapping.get(extension, extension)
        extension = super(GeverFileNameNormalizer, self).normalize(extension)
        extension = extension.lower()
        return extension

    def normalize(self, filename, extension=None):
        """if the extension is not passed separately, it will
        be determined from the filename (if possible).
        """
        if extension is None:
            filename, extension = self.split_filename_extension(filename)
        filename = self.normalize_name(filename)
        if extension:
            if extension.startswith("."):
                extension = extension[1:]
            extension = self.normalize_extension(extension)
            return ".".join((filename, extension))
        return filename


filenamenormalizer = GeverFileNameNormalizer()
