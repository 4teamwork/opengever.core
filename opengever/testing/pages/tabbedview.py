from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.queryinfo import QueryInfo


def tabs(browser=default_browser):
    """Return the tabbedview tab link nodes.
    """
    return browser.css('.tabbedview-tabs > ul.formTabs > li.formTab > a')


@QueryInfo.build
def open(label, browser=default_browser, query_info=None):
    """Open a tab by label.
    The browser must be opened on the tabbed view and the tab must be visible.
    """
    href = get_link(label, browser=browser, query_info=query_info).attrib.get('href')
    assert href.startswith('#'), 'Unexpected href of tab link node.'
    view = 'tabbedview_view-{}'.format(href[1:])
    browser.open(browser.context, view=view)


@QueryInfo.build
def get_link(label, browser=default_browser, query_info=None):
    """Return a tab link by label.
    The browser must be opened on the tabbed view and the tab must be visible.
    """
    for link in tabs(browser=browser):
        if link.text == label:
            return link

    query_info.add_hint('Visible tabs: {!r}'.format(tabs(browser=browser).text))
    raise NoElementFound(query_info)


def major_actions(browser=default_browser):
    """Return a list of major action link nodes.
    """
    return browser.css('.tabbedview-action-list > li > a')


def minor_actions(browser=default_browser):
    """Return a list of minor action link nodes (those in the menu).
    """
    return browser.css('dl#plone-contentmenu-tabbedview-actions > dd li > a')


@QueryInfo.build
def row_for(obj, browser=default_browser, query_info=None):
    """Return the row representing an object.
    In order for this to work, it is required that there is a checkbox with this
    path as value.
    """
    table = browser.css('#listing_container table.listing').first
    if table.css('input[name="task_ids:list"]'):
        return row_by_task_id(obj.get_sql_object().task_id,
                              browser=browser, query_info=query_info)
    else:
        return row_by_path('/'.join(obj.getPhysicalPath()),
                           browser=browser, query_info=query_info)


@QueryInfo.build
def row_by_path(path, browser=default_browser, query_info=None):
    """Return the row representing an object identified by path.
    In order for this to work, it is required that there is a checkbox with this
    path as value.
    """
    table = browser.css('#listing_container table.listing').first
    checkboxes = table.css('input[name="paths:list"]')
    for checkbox in checkboxes:
        if checkbox.attrib.get('value') == path:
            return checkbox.parent('tr')

    query_info.add_hint('Paths: {!r}'.format(
        [box.attrib.get('value') for box in checkboxes]))
    raise NoElementFound(query_info)


@QueryInfo.build
def row_by_task_id(task_id, browser=default_browser, query_info=None):
    """Return the row representing an object identified by task id.
    In order for this to work, it is required that there is a task_ids-checkbox.
    """
    table = browser.css('#listing_container table.listing').first
    checkboxes = table.css('input[name="task_ids:list"]')
    for checkbox in checkboxes:
        if checkbox.attrib.get('value') == str(task_id):
            return checkbox.parent('tr')

    query_info.add_hint('Task IDs: {!r}'.format(
        [box.attrib.get('value') for box in checkboxes]))
    raise NoElementFound(query_info)


@QueryInfo.build
def cell_for(obj, column_title, browser=default_browser, query_info=None):
    """Return the cell for a column in a row representing an object.
    In order for this to work, it is required that there is a checkbox with this
    path as value.
    """
    row = row_for(obj, browser=browser, query_info=query_info)
    table = row.parent('table')
    if column_title not in table.titles:
        query_info.add_hint('Column title {!r} not found.\nTitles: {!r}'.format(
            column_title, table.titles))
        raise NoElementFound(query_info)

    return row.cells[table.titles.index(column_title)]
