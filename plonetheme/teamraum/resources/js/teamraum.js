jQuery(function($) {
  $('#portal-globalnav li.selected a').append('<div class="triangle">&nbsp;</div>');

  var tabs_menu = $('<a href="#" class="toggleTabs">▼</a>');
  tabs_menu.click(function(e){
    e.preventDefault();
    $('#content li.formTab a').not('.selected').toggleClass('visible');
  });
  $('#content ul.formTabs').after(tabs_menu);

  $('#content li.formTab a').not('.selected').click(function(){
    $('#content li.formTab a.visible').removeClass('visible');
  });

  $('#customstyles-reset-form input[type="submit"]').click(function(e){
    e.preventDefault();
    if (confirm('Do you really want to reset?')) {
      $('#customstyles-reset-form').submit();
    }
  });

  // Placeholder fallback for IE <= 9
  function add_placeholder() {
    var me = $(this);
    if(me.val() === ''){
      me.val(me.attr('placeholder')).addClass('placeholder');
    }
  }
  function remove_placeholder() {
    var me = $(this);
    if(me.val() === me.attr('placeholder')){
      me.val('').removeClass('placeholder');
    }
  }

  // Create a dummy element for feature detection
  if (!('placeholder' in $('<input>')[0])) {

    // Select the elements that have a placeholder attribute
    $('input[placeholder], textarea[placeholder]').blur(add_placeholder).focus(remove_placeholder).each(add_placeholder);

    // Remove the placeholder text before the form is submitted
    $('form').submit(function(){
      $(this).find('input[placeholder], textarea[placeholder]').each(remove_placeholder);
    });
  }

  // dropdown_button
  $('dl.dropdown_button dt').live('click', function(e){
    e.preventDefault();
    $(this).parent('dl').toggleClass('active');
  });
  $('body').click(function(e){
    if (!$(e.target).closest("dl.dropdown_button.active").length) {
      $('dl.dropdown_button.active').removeClass('active');
    }
  });
});
