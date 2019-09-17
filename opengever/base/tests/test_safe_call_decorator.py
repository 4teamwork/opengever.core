from opengever.base.request import tracebackify
from Products.Five.browser import BrowserView
from unittest import TestCase
from ZODB.POSException import ConflictError
from zope.publisher.browser import TestRequest


@tracebackify
class ValidView(BrowserView):
    def __call__(self):
        return 'OK'


@tracebackify
class RaiseErrorView(BrowserView):
    def __call__(self):
        raise


@tracebackify
class RaiseConflictErrorErrorView(BrowserView):
    def __call__(self):
        raise ConflictError


@tracebackify
class RaiseKeyboardInterruptErrorView(BrowserView):
    def __call__(self):
        raise KeyboardInterrupt


@tracebackify(to_re_raise=ValueError)
class RaiseValueErrorErrorView(BrowserView):
    def __call__(self):
        raise ValueError


@tracebackify(to_re_raise=[ValueError, KeyError])
class RaiseMultipleErrorView(BrowserView):
    def __call__(self, keyerror):
        if keyerror:
            raise KeyError
        else:
            raise ValueError


class TestSafeCallDecorator(TestCase):

    def test_return_subclass(self):
        self.assertTrue(issubclass(ValidView, BrowserView))

    def test_decorated_view_name_is_preserved(self):
        self.assertEquals('ValidView', ValidView.__name__)

    def test_decorated_view_module_is_preserved(self):
        self.assertEquals('opengever.base.tests.test_safe_call_decorator',
                          ValidView.__module__)

    def test_exceptions_gets_catched_and_returned(self):
        view = RaiseErrorView(object(), TestRequest())
        self.assertTrue(view().startswith('Traceback (most recent call last)'))

    def test_conflicterror_raises(self):
        with self.assertRaises(ConflictError):
            RaiseConflictErrorErrorView(object(), TestRequest())()

    def test_keyboardinterrupt_raises(self):
        with self.assertRaises(KeyboardInterrupt):
            RaiseKeyboardInterruptErrorView(object(), TestRequest())()

    def test_raise_single_additional_exceptions(self):
        with self.assertRaises(ValueError):
            RaiseValueErrorErrorView(object(), TestRequest())()

    def test_raise_multiple_additional_exceptions(self):
        with self.assertRaises(ValueError):
            RaiseMultipleErrorView(object(), TestRequest())(keyerror=False)

        with self.assertRaises(KeyError):
            RaiseMultipleErrorView(object(), TestRequest())(keyerror=True)
