from ftw.testbrowser import browser as default_browser


def sharing_tab_data(browser=default_browser):
    """Returns data from the sharing tab matrix (without table headers) as
    a list of lists. Checkbox cells are converted to simple True or False
    values.
    """

    sharing_data = []
    table = browser.css('table#user-group-sharing').first
    for row in table.body_rows:
        rowdata = []
        for td in row.css('td'):
            if td.classes == ['listingCheckbox']:
                spans = td.css('span')
                if spans and spans.first.classes == ['function-ok']:
                    rowdata.append(True)
                else:
                    rowdata.append(False)
            else:
                rowdata.append(td.text)
        sharing_data.append(rowdata)
    return sharing_data
