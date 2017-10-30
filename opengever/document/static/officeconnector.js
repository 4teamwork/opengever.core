(function($) {

    "use strict";

    var APPLICATION_TIMEOUTS = {
        officeconnector: 5 * 1000,
        officeatwork: 45 * 1000,
    };

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

    function requestJSON(url, method) {
        method = method || 'GET';

        return $.ajax(url, {
            headers: {
                Accept: "application/json",
            },
            type: method,
        });

    }

    function isDocumentLocked(documentURL) {
        return requestJSON(documentURL + "/status").pipe(function(data) {
            return JSON.parse(data).locked;
        });
    }

    function checkout(documentURL) {
        return poll(function() {
            return isDocumentLocked(documentURL);
        });
    }

    function edit(application) {
        var promise = $.Deferred();

        setTimeout(function() {
            promise.reject();
        }, APPLICATION_TIMEOUTS[application]);

        return promise;
    }

    function delete_confirmation_modal(data, documentURL) {
        var labels = JSON.parse(data);
        var title = labels.title;
        var message = labels.message;
        var label_yes = labels.label_yes;
        var label_no = labels.label_no;

        // IE11 does not support computed properties
        // The introduction order of the buttons dictionary is left to right
        var buttons = {};
        buttons[label_no] = function() { $(this).dialog('close'); };
        buttons[label_yes] = function() { delete_shadow_document(documentURL); };

        $('<div id="dialog">' + JSON.parse(data).message + '</div>').dialog({
            draggable: false,
            modal: true,
            title: title,
            buttons: buttons,
        });
    }

    function delete_shadow_document(documentURL) {
        var delete_status = requestJSON(documentURL + '/delete_shadow_document', 'DELETE');
        $.when(delete_status.done(), delete_status.fail())
        .then(function(data) { window.location.replace(JSON.parse(data[0]).parent_url); })
        // There should be a portal message set
        .fail(function(){ location.reload(); });
    }

    function show_status_modal(data) {
        var labels = JSON.parse(data);
        var title = labels.title;
        var message = labels.message;

        $('<div id="dialog" class="officeatwork-status oc-loading">' + message + '</div>').dialog({
            draggable: false,
            modal: true,
            title: title,
        });
    }

    function handle_officeatwork_timeout(documentURL) {
        var retry_abort_labels = requestJSON(documentURL + '/oaw_retry_abort_labels');
        $.when(retry_abort_labels.done()).then(function(data) { render_retry_abort_labels(data); });
    }

    function render_retry_abort_labels(data) {
        var labels = JSON.parse(data);
        var retry = labels.retry;
        var abort = labels.abort;

        var officeatworkStatusDiv = $('div.officeatwork-status');
        officeatworkStatusDiv.removeClass('oc-loading');
        officeatworkStatusDiv.empty();
        officeatworkStatusDiv.append('<a class="officeatwork-retry" href="">'+ retry + '</a>');
        officeatworkStatusDiv.append('<a class="officeatwork-abort" href="">' + abort + '</a>');
    }

    $(document).on("click", ".oc-checkout", function(event) {
        var checkoutButton = $(event.currentTarget);
        var documentURL = checkoutButton.data("document-url");

        if(checkoutButton.hasClass('oc-loading')) {
            return false;
        }

        checkoutButton.addClass("oc-loading");

        isDocumentLocked(documentURL).pipe(function(status) {
            if(status) {
                return edit('officeconnector');
            } else {
                return checkout(documentURL);
            }
        })
        .done(function() { location.reload(); })
        .fail(function() { checkoutButton.removeClass("oc-loading"); });
    });

    $(document).on("click", ".officeatwork-abort", function(event) {
        var loc = document.location;
        var documentURL = loc.protocol + '//' + loc.hostname + ':' + loc.port + loc.pathname;

        var delete_confirmation = requestJSON(documentURL + '/delete_confirm');
        $.when(delete_confirmation.done()).then(function(data) { delete_confirmation_modal(data, documentURL); });

        return false;
    });

    $(document).on("click", ".officeatwork-retry", function(event) {
        // This relies on the query string as the element will not be there otherwise
        location.reload();
        return false;
    });

    $(document).on('reload', '.tabbedview_view', function(event) {
        var loc = document.location;
        var params = new URLSearchParams(loc.search);
        if ( params.get('oaw_init') ) {
            var documentURL = loc.protocol + '//' + loc.hostname + ':' + loc.port + loc.pathname;

            var oaw_dialog_labels = requestJSON(documentURL + '/oaw_init_labels');

            $.when(oaw_dialog_labels.done()).then(function(data) { show_status_modal(data); });

            var document_lock = isDocumentLocked(documentURL).pipe(function(status) {
                if(!status) {
                    return edit('officeatwork');
                }

                else {
                    return checkout(documentURL);
                }
            });

            /*
            Office Connector has succesfully:
            1) Initiated the template chooser
            2) Generated a document
            3) Uploaded the document
            4) Initiated a checkout
            5) Locked the document
            */
            $.when(document_lock.done(), document_lock.fail())
            .then(function() { location.reload(); })
            .fail(function() { handle_officeatwork_timeout(documentURL); } );
        }
    });

})(window.jQuery);

function openOfficeconnector(data) {
    // URLs the browser does not handle get passed onto the OS
    window.location = data.url;
}

function alertUser(data) {
    alert(JSON.parse(data.responseText.error.message));
}

function officeConnectorCheckout(url) {
    var officeconnector_config = {};

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers.accept = 'application/json';

    $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
}

function officeConnectorAttach(url) {
    var officeconnector_config = {};

    officeconnector_config.url = url;
    officeconnector_config.headers = {};
    officeconnector_config.headers.accept = 'application/json';

    $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
}

function officeConnectorMultiAttach(url) {
    var officeconnector_config = {};

    officeconnector_config.data = {};
    officeconnector_config.data.documents = [];
    officeconnector_config.dataType = 'json';
    officeconnector_config.headers = {};
    officeconnector_config.headers.accept = 'application/json';
    officeconnector_config.headers['Content-Type'] = 'application/json';
    officeconnector_config.type = 'POST';
    officeconnector_config.url = url;

    $('form[name="tabbedview_form"] :checkbox').each(function(i, checkbox) {
        if (checkbox.checked) {
            officeconnector_config.data.documents.push(checkbox.value);
        }
    });

    if (officeconnector_config.data.documents.length > 0) {
        var dossier_config = {};

        dossier_config.dataType = 'json';
        dossier_config.headers = {};
        dossier_config.headers.accept = 'application/json';
        dossier_config.type = 'GET';
        dossier_config.url = window.location.pathname + '/attributes';

        dossier_attributes = $.ajax(dossier_config);

        $.when(dossier_attributes.done()).then(function(attributes){ officeconnector_config.data.bcc = attributes.email; });

        $.when(dossier_attributes.always()).then(function(){
            officeconnector_config.data = JSON.stringify(officeconnector_config.data);
            $.ajax(officeconnector_config).error(alertUser).done(openOfficeconnector);
        });
    }
}
