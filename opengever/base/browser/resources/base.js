$(window).load(function(){
  // set focus on first form field
  var firstFormElement = $("form#form input:text:visible, form#form textarea:visible, .keyword-widget").first();
  // Check if element is select2 widget
  if (firstFormElement.data('select2')) {
    firstFormElement.focus();
    firstFormElement.select2('focus');
  } else {
    firstFormElement.focus();
  }
});

$(document).delegate('body', 'tabbedview.unknownresponse', function(event, overview, jqXHR) {
  if (jqXHR.getResponseHeader('X-GEVER-Service') === 'Portal') {
    // the response we got originates from a portal, we reload to show the login window
    location.reload();
    return false;
  }
});
