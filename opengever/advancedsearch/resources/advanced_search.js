$(function(){

  // initalize
  if($('input[name=form.widgets.object_provides:list]:checked').length === 0){
    $('input[name=form.widgets.object_provides:list]:first').click();
  }

  // add manually the class for some fields, where the addClass function not work (autocomplete widget ect.)
  $('#form-widgets-responsible-autocomplete').addClass('opengever-dossier-behaviors-dossier-IDossierMarker');
  $('#form-widgets-review_state-from').addClass('opengever-dossier-behaviors-dossier-IDossierMarker');
  $('#form-widgets-checked_out-autocomplete').addClass('opengever-document-behaviors-IBaseDocument');
  $('#form-widgets-trashed-0').addClass('opengever-document-behaviors-IBaseDocument');
  $('#form-widgets-issuer-autocomplete').addClass('opengever-task-task-ITask');

  $('input[name=form.widgets.object_provides:list]').change(function(){
    var types = ['opengever-dossier-behaviors-dossier-IDossierMarker', 'opengever-task-task-ITask', 'opengever-document-behaviors-IBaseDocument'];
    selected = $('input[name=form.widgets.object_provides:list]:checked').attr('value').replace(/\./g, '-');
    types.remove(selected);

    // show current
    $('.'+selected).each(function(){
      $(this).parents('.field:first').show();
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
  // submit the form manualy when the enter key was pressed.
  $('#form').find('input').keydown(function(e){
    if (e.keyCode == 13) {
      if ($(this).attr('class').indexOf('ui-autocomplete-input') == -1){
        $('#form').submit();
        return false;
      }
    }
  });
});
