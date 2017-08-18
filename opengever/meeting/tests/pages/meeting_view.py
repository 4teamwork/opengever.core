from ftw.testbrowser import browser
from operator import methodcaller


def metadata(**kwargs):
    """Return the meeting metadata as lists of labels and values.
    """
    return reduce(list.__add__,
                  map(methodcaller('lists', **kwargs),
                      browser.css('table.meeting-metadata')))
