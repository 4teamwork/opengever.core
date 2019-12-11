from opengever.workspace.invitation import valid_email
import unittest


class TestUnitEmailValidator(unittest.TestCase):

    def assert_valid(self, value):
        self.assertTrue(valid_email(value))

    def assert_invalid(self, value):
        self.assertFalse(valid_email(value))

    def test_invalid_email_empty(self):
        self.assert_invalid('')

    def test_invalid_email_no_at(self):
        self.assert_invalid('foobarqux.com')

    def test_invalid_email_trailing_at(self):
        self.assert_invalid('foO@')

    def test_invalid_email_leading_at(self):
        self.assert_invalid('@foO')

    def test_invalid_email_too_many_at(self):
        self.assert_invalid('foo@bar@qux')

    def test_valid_email_shortest(self):
        self.assert_valid('a@b')

    def test_valid_email_simple(self):
        self.assert_valid('email@example.com')

    def test_valid_email_firstname_lastname(self):
        self.assert_valid('firstname.lastname@example.com')

    def test_valid_email_plus(self):
        self.assert_valid('user+mailbox@example.com')
