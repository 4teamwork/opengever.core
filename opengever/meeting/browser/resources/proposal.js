(function(global, $,SelectAutocomplete) {

  $(function() {
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      new SelectAutocomplete({
          target: 'select#form-widgets-committee, select#form-widgets-language, select#form-widgets-member'});
    }
  });

}(window, jQuery, window.SelectAutocomplete));
