from ftw.testbrowser import browser
from opengever.testing.pages import byline


def metadata(**kwargs):
    """Return the meeting metadata as a dict of labels and values.
    """
    data = byline.text_dict()
    for table in browser.css('table.meeting-metadata'):
        for row in table.lists():
            data[row[0]] = row[1]
    return data
