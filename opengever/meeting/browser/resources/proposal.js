(function(global, $,SelectAutocomplete) {

  $(function() {
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      new SelectAutocomplete({
          target: 'select#form-widgets-committee, select#form-widgets-language, select#form-widgets-member'});
    }

    // hide proposal document by default
    $('#formfield-form-widgets-proposal_document').hide();

    $("input[name='form.widgets.proposal_document_type']").change(function(){
      if (this.value === 'existing'){
        $('#formfield-form-widgets-proposal_document').show();
        $('#formfield-form-widgets-proposal_template').hide();
      } else {
        $('#formfield-form-widgets-proposal_document').hide();
        $('#formfield-form-widgets-proposal_template').show();
      }
    })

  });

}(window, jQuery, window.SelectAutocomplete));
