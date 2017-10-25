from ftw.testbrowser import browser as default_browser


def text_dict(browser=default_browser):
    return dict(text_items(browser=browser))


def text_items(browser=default_browser):
    result = []
    for label_node, text_node in items(browser=browser):
        result.append((label_node.text, text_node.text))
    return result


def items(browser=default_browser):
    items = []
    for li in div(browser=browser).css('>ul>li'):
        label, content = li.css('>*')
        items.append((label, content))

    return items


def by_label(browser=default_browser):
    return {label_node.text: text_node
            for label_node, text_node in items(browser=browser)}


def div(browser=default_browser):
    return browser.css('.documentByLine').first
