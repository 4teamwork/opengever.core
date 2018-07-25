(function(global, $,SelectAutocomplete) {

  $(function() {
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      new SelectAutocomplete({
          target: 'select#form-widgets-committee, select#form-widgets-language, select#form-widgets-member'});
    }

    document_type_widget = $('input[name="form.widgets.proposal_document_type"]');
    if(document_type_widget.length) {
      selected_document_type = document_type_widget
      .filter(function(index, el) { return el.checked })[0].value;

      proposal_template = $('#formfield-form-widgets-proposal_template');
      proposal_document = $('#formfield-form-widgets-proposal_document');

      switch(selected_document_type) {
        case 'template':
          proposal_document.hide();
          break;
        case 'existing':
          proposal_template.hide();
          break;
      }

      document_type_widget.change(function(){
        proposal_template.toggle();
        proposal_document.toggle();
      });
    }

  });

}(window, jQuery, window.SelectAutocomplete));
