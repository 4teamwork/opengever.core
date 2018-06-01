(function(global, $,SelectAutocomplete) {

  $(function() {
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      new SelectAutocomplete();
    }
  });

}(window, jQuery, window.SelectAutocomplete));
