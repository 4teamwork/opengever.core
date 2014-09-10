jQuery(function($) {
    // Toggle orgunitselector menu
    $('#toggle_orgunitselector').click(function(e){
      e.preventDefault();
      var me = $(this)
      close_opened(me);
      me.toggleClass('selected');
      $('#portal-orgunit-selector dd.actionMenuContent').toggle();
    });
});