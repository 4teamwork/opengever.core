def assert_equal(expected, actual):
    try:
        assert expected == actual
    except AssertionError:
        print "\nAssertionError: Items not equal"
        print "Expected: %s" % expected
        print "Actual: %s" % actual
        raise


def assert_in(needle, haystack):
    try:
        assert needle in haystack
    except AssertionError:
        print "\nAssertionError: Unable to find needle in haystack."
        print "Needle: %r" % needle
        print "Haystack: %r" % haystack
        raise
