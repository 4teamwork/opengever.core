function openOfficeconnector(data) {
    // URLs the browser does not handle get passed onto the OS
    window.location = data['url'];
}

var officeconnector_config = {
    headers: { Accept: 'application/json' },
    url: ''
}

function officeConnectorCheckout(url) {
    officeconnector_config.url = url;
    $.ajax(officeconnector_config).done(openOfficeconnector);
}

function officeConnectorAttach(url) {
    officeconnector_config.url = url;
    $.ajax(officeconnector_config).done(openOfficeconnector);
}
