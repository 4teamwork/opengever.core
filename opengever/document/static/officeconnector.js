function openOfficeconnector(data) {
    // URLs the browser does not handle get passed onto the OS
    window.location = data['url'];
}

function officeConnectorCheckout(url) {
    var officeconnector_config = {}

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers['Accept'] = 'application/json';

    $.ajax(officeconnector_config).done(openOfficeconnector);
}

function officeConnectorAttach(url) {
    var officeconnector_config = {}

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers['Accept'] = 'application/json';

    $.ajax(officeconnector_config).done(openOfficeconnector);
}
