(function($) {

    "use strict";

    var OFFICE_CONNECTOR_TIMEOUT = 5 * 1000;

    function poll(fn, options) {

        options = $.extend({
            interval: 2 * 1000,
            timeout: 15 * 1000
        }, options);

        var promise = $.Deferred();
        var endTime = new Date().getTime() + options.timeout;

        function checkCondition() {
            $.when(fn()).done(function(proceed) {
                if(proceed) {
                    promise.resolve();
                } else if(new Date().getTime() < endTime) {
                    setTimeout(checkCondition, options.interval);
                } else {
                    promise.reject(new Error("Polling timed out using timeout of: " + options.timeout + "ms"));
                }
            });
        }

        checkCondition();

        return promise;
    }

    function requestJSON(url) {
        return $.ajax(url, {
            headers: {
                Accept: "application/json",
            }
        });
    }

    function isDocumentCheckedOut(documentURL) {
        return requestJSON(documentURL + "/status").pipe(function(data) {
            return JSON.parse(data)["checked_out"];
        });
    }

    function checkout(documentURL) {
        return poll(function() {
            return isDocumentCheckedOut(documentURL)
        });
    }

    function edit() {
        var promise = $.Deferred();
        setTimeout(function() {
            promise.reject();
        }, OFFICE_CONNECTOR_TIMEOUT);
        return promise;
    }

    $(document).on("click", ".oc-checkout", function(event) {
        var checkoutButton = $(event.currentTarget);
        var documentURL = checkoutButton.data("document-url");
        if(checkoutButton.hasClass('oc-loading')) {
            return false;
        }
        checkoutButton.addClass("oc-loading");
        isDocumentCheckedOut(documentURL).pipe(function(status) {
            if(status) {
                return edit();
            } else {
                return checkout(documentURL);
            }
        })
        .done(function() { location.reload(); })
        .fail(function() {
            checkoutButton.removeClass("oc-loading");
        });
    });

})(window.jQuery);

function openOfficeconnector(data) {
    // URLs the browser does not handle get passed onto the OS
    window.location = data['url'];
}

function alertUser(data) {
    alert(JSON.parse(data["responseText"])["error"]["message"]);
}

function officeConnectorCheckout(url) {
    var officeconnector_config = {}

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers['Accept'] = 'application/json';

    $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
}

function officeConnectorAttach(url) {
    var officeconnector_config = {}

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers['Accept'] = 'application/json';

    $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
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
        $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
    }

}
