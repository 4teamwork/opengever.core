$(function(){

  // initalize
  if($("input[name='form.widgets.object_provides']:checked").length === 0){
    $("input[name='form.widgets.object_provides']:first").click();
  }

  // add manually the class for some fields, where the addClass function not work (autocomplete widget ect.)
  $('#form-widgets-review_state-from').addClass('opengever-dossier-behaviors-dossier-IDossierMarker');
  $('#form-widgets-trashed-0').addClass('opengever-document-behaviors-IBaseDocument');

  $("input[name='form.widgets.object_provides']").change(function(){
    var types = ['opengever-dossier-behaviors-dossier-IDossierMarker', 'opengever-task-task-ITask', 'opengever-document-behaviors-IBaseDocument'];
    selected = $("input[name='form.widgets.object_provides']:checked").attr('value').replace(/\./g, '-');
    types.splice(types.indexOf(selected),1);

    // show current
    $('.'+selected).each(function(){
      $(this).parents('.field:first').show();

    $('.keyword-widget:visible').each(function(index, widget){
        window.ftwKeywordWidget.initWidget($(widget));
    });

    });

    //hide others
    $(types).each(function(){
      $('.'+this).each(function(){
        $(this).parents('.field:first').hide();
      });
    });
  }).change();

  // ie workaround for fix the submit on enter functionality
  // needed that z3c form call the rigth button handler.
  $('#form').append('<input type="hidden" name="form.buttons.button_search" value="Search" />');
});
