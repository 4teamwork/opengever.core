from opengever.base.model import FILENAME_LENGTH
from opengever.base.filename import GeverFileNameNormalizer
from unittest import TestCase
import string
import sys
import unicodedata


class TestFilenameNormalizer(TestCase):

    normalizer = GeverFileNameNormalizer()
    allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _.,=()+-'
    max_length = 100

    def test_character_cases_are_retained(self):
        self.assertEqual(string.ascii_letters,
                         self.normalizer.normalize_name(unicode(string.ascii_letters)))

    def test_maximal_filename_length(self):
        filename = u''.join('a' for i in range(2 * self.max_length))
        self.assertEqual(self.max_length,
                         len(self.normalizer.normalize_name(filename)))

    def test_filename_in_favorites_can_handle_long_filename(self):
        filename = u''.join('a' for i in range(2 * self.max_length))
        self.assertTrue(
            len(self.normalizer.normalize_name(filename)) < FILENAME_LENGTH)

    def test_filename_in_favorites_can_handle_long_filename_with_extension(self):
        filename = u''.join('a' for i in range(2 * self.max_length)) + ".jpeg"
        self.assertTrue(
            len(self.normalizer.normalize_name(filename)) < FILENAME_LENGTH)

    def test_filename_in_favorites_can_handle_long_filename_with_long_extension(self):
        basename = u''.join('a' for i in range(2 * self.max_length))
        filename = ".".join((basename, basename))
        self.assertTrue(
            len(self.normalizer.normalize_name(filename)) < FILENAME_LENGTH)

    def test_filename_cropping_happens_after_character_mapping(self):
        filename = u''.join(u'\xe4' for i in range(2 * self.max_length))
        self.assertEqual(self.max_length,
                         len(self.normalizer.normalize_name(filename)))

    def test_filename_cropping_happens_after_character_decoding(self):
        filename = u''.join(u'\xe6' for i in range(2 * self.max_length))
        self.assertEqual(self.max_length,
                         len(self.normalizer.normalize_name(filename)))

    def test_filename_cropping_happens_after_consecutive_spaces_elimination(self):
        filename = u''.join(u'  aa' for i in range(2 * self.max_length))
        self.assertEqual(self.max_length,
                         len(self.normalizer.normalize_name(filename)))

    def test_filename_cropped_length_does_not_include_file_extension(self):
        filename = u''.join(u'\xe4' for i in range(2 * self.max_length))
        extension = '.txt'
        expected_length = self.max_length + len(extension)
        self.assertEqual(expected_length,
                         len(self.normalizer.normalize(filename+extension)))

    def test_normalizer_handles_non_unicode_strings(self):
        self.assertTrue(isinstance(self.normalizer.normalize("a non unicode string"), unicode))

    def test_only_allowed_characters_are_output(self):
        for i in range(sys.maxunicode):
            normalized = self.normalizer.normalize_name(unichr(i))
            for character in normalized:
                self.assertTrue(character in self.allowed_characters,
                                u"unichr({}): {} was normalized to {}".format(i, unichr(i), normalized))

    def test_consecutive_spaces_are_cleaned_up(self):
        self.assertEqual(u'a test name with spaces',
                         self.normalizer.normalize_name(u'a test  name with   spaces'))
        self.assertEqual(u'a test name with spaces',
                         self.normalizer.normalize_name(u'a test \t name with ;  spaces'))

    def test_german_umlaut_mapping(self):
        mapping = ((u'\xe4', 'ae'), (u'\xfc', 'ue'), (u'\xf6', 'oe'),
                   (u'\xc4', 'Ae'), (u'\xdc', 'Ue'), (u'\xd6', 'Oe'),
                   (u'\xdf', 'ss'))
        for special, normalized in mapping:
            self.assertEqual(normalized,
                             self.normalizer.normalize_name(special))

    def test_german_umlaut_mapping_also_works_for_decomposed_characters(self):
        mapping = ((u'\xe4', 'ae'), (u'\xfc', 'ue'), (u'\xf6', 'oe'),
                   (u'\xc4', 'Ae'), (u'\xdc', 'Ue'), (u'\xd6', 'Oe'),
                   (u'\xdf', 'ss'))
        for special, normalized in mapping:
            decomposed = unicodedata.normalize('NFKD', special)
            self.assertEqual(normalized,
                             self.normalizer.normalize_name(decomposed))

    def test_french_accent_mapping(self):
        mapping = ((u'\xe9', 'e'), (u'\xe8', 'e'), (u'\xea', 'e'),
                   (u'\xc9', 'E'), (u'\xc8', 'E'), (u'\xca', 'E'),
                   (u'\xe0', 'a'), (u'\xe2', 'a'),
                   (u'\xc0', 'A'), (u'\xc2', 'A'),
                   (u'\xf4', 'o'), (u'\u0153', 'oe'),
                   (u'\xd4', 'O'), (u'\u0152', 'OE'),
                   (u'\xfb', 'u'), (u'\xf9', 'u'),
                   (u'\xdb', 'U'), (u'\xd9', 'U'),
                   (u'\xee', 'i'), (u'\xef', 'i'),
                   (u'\xce', 'I'), (u'\xcf', 'I'),
                   (u'\xe7', 'c'), (u'\xc7', 'C'))
        for special, normalized in mapping:
            self.assertEqual(normalized,
                             self.normalizer.normalize_name(special))

    def test_special_character_mapping(self):
        mapping = ((u'&', u'+'),)
        for special, normalized in mapping:
            self.assertEqual(normalized,
                             self.normalizer.normalize_name(special))

    def test_extension_mapping(self):
        mapping = ((u'tiff', u'tif'), (u'jpeg', u'jpg'))
        for original, mapped in mapping:
            self.assertEqual(mapped,
                             self.normalizer.normalize_extension(original))

    def test_unmapped_extensions_remain_unchanged(self):
        extension_list = [u'docx', u'doc', u'txt', u'png', u'xls', u'xlsx', u'ppt', u'pptx']
        for extension in extension_list:
            self.assertEqual(extension,
                             self.normalizer.normalize_extension(extension))

    def test_split_filename_extension_works_for_length_up_to_4_characters(self):
        self.assertEqual((u'filename', u'txt'),
                         self.normalizer.split_filename_extension(u'filename.txt'))
        self.assertEqual((u'filename', u'jpeg'),
                         self.normalizer.split_filename_extension(u'filename.jpeg'))
        self.assertEqual((u'my.jpegs', ''),
                         self.normalizer.split_filename_extension(u'my.jpegs'))

    def test_normalizer_handles_dotted_filenames(self):
        filename = "my.dotted.file.name.ext"
        self.assertEqual(u'my.dotted.file.name.ext',
                         self.normalizer.normalize_name(filename))
        self.assertEqual((u'my.dotted.file.name', 'ext'),
                         self.normalizer.split_filename_extension(filename))

    def test_filename_normalization(self):
        self.assertEqual(u'Uebersicht.txt', self.normalizer.normalize(u'\xdcbersicht.txt'))
        self.assertEqual(u'Uebersicht.txt', self.normalizer.normalize(u'\xdcbersicht', extension=u'txt'))
        self.assertEqual(u'Filename.tif', self.normalizer.normalize(u'Filename.tiff'))
        self.assertEqual(u'Filename.tif', self.normalizer.normalize(u'Filename', extension=u'tiff'))

    def test_leading_and_trailing_whitespaces_are_removed(self):
        self.assertEqual("filename.txt", self.normalizer.normalize("  filename  .txt"))
        self.assertEqual("filename.txt", self.normalizer.normalize("[filename].txt"))
        self.assertEqual("filename.txt", self.normalizer.normalize("[filename]", extension="txt"))
