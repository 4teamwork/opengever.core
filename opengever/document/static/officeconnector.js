function openOfficeconnector(data) {
    // URLs the browser does not handle get passed onto the OS
    window.location = 'officeconnector:' + JSON.parse(data)['token'];
}

var officeconnector_config = {
    headers: { Accept: 'application/json' },
    url: ''
}

$(document).on('click', '#officeconnector-attach-url', function(event){
    event.preventDefault();
    officeconnector_config.url = $('#officeconnector-attach-url').data('officeconnectorAttachTokenUrl');
    $.ajax(officeconnector_config).done(openOfficeconnector);
});

$(document).on('click', '#officeconnector-checkout-url', function(event){
    event.preventDefault();
    officeconnector_config.url = $('#officeconnector-checkout-url').data('officeconnectorCheckoutTokenUrl')
    $.ajax(officeconnector_config).done(openOfficeconnector);
});
