$(function() {
  // set focus on first form field
  $("form#form input:text:visible, form#form textarea:visible").first().focus();
});


$(document).delegate('body', 'tabbedview.unknownresponse', function(event, overview, jqXHR) {
  if (jqXHR.getResponseHeader('X-GEVER-Service') === 'Portal') {
    // the response we got originates from a portal, we reload to show the login window
    location.reload();
    return false;
  }
});
