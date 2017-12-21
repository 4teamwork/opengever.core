from ftw.testbrowser import browser as default_browser


def portaltabs(browser=default_browser):
    return browser.css('#portal-globalnav li a')
