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

function officeConnectorMultiAttach(url) {
    var officeconnector_config = {}

    officeconnector_config.data = [];
    officeconnector_config.dataType = 'json';
    officeconnector_config.headers = {};
    officeconnector_config.headers['Accept'] = 'application/json';
    officeconnector_config.headers['Content-Type'] = 'application/json';
    officeconnector_config.type = 'POST';
    officeconnector_config.url = url;

    $('form[name="tabbedview_form"] :checkbox').each(function(i, checkbox) {
        if (checkbox.checked) {
            officeconnector_config.data.push(checkbox.value);
        }
    });


    if (officeconnector_config.data.length > 0) {
        officeconnector_config.data = JSON.stringify(officeconnector_config.data);
        $.ajax(officeconnector_config).done(openOfficeconnector);
    }

}
