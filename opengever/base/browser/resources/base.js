$(window).load(function(){
  // set focus on first form field
  var firstFormElement = $('form#form input:text:visible, form#form textarea:visible, .keyword-widget').first();
  // Check if element is select2 widget
  if (firstFormElement.data('select2')) {
    firstFormElement.focus();
    firstFormElement.select2('focus');
  } else {
    firstFormElement.focus();
  }

  // Handle reminder_option-date visibility in task response form
  function handleReminderOptionsDateChooserVisiblity(optionType) {
    var optionTypeCalendarField = $('#formfield-form-widgets-reminder_option_date');
    if (optionType === 'on_date') {
      optionTypeCalendarField.show();
    } else {
      optionTypeCalendarField.hide();
    }
  }
  var reminderOptionsForm = $('#form-widgets-reminder_option');
  if (reminderOptionsForm.length) {
    var currentOptionType = reminderOptionsForm[0].options[reminderOptionsForm[0].selectedIndex].value;
    handleReminderOptionsDateChooserVisiblity(currentOptionType);
    reminderOptionsForm.on('change', function(e) {
      var optionType = e.target.options[e.target.selectedIndex].value;
      handleReminderOptionsDateChooserVisiblity(optionType);
    });
  }


});

$(document).delegate('body', 'tabbedview.unknownresponse', function(event, overview, jqXHR) {
  if (jqXHR.getResponseHeader('X-GEVER-Service') === 'Portal') {
    // the response we got originates from a portal, we reload to show the login window
    location.reload();
    return false;
  }
});


/**
 * Gever UI-Switcher. This function will be called by a user-action to switch
 * to the new gever-ui.
 */
function switchUI(){
  setTourAsSeen('be_new_frontend_teaser');
  var pathname = new URL($('body').data('portal-url')).pathname;
  Cookies.set('geverui', '1', {path: pathname, expires: 365});
  window.location.reload(true);
}
