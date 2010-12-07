jq(function(){

  $('#form-controls input[name=save]').toggle();

  //test global overwrite
  $.fn.ftwtable.defaults.onBeforeLoad = function(){
  };

  // initialize table
  table = $('#template_chooser').ftwtable({
    'url' : '@@add-tasktemplate/listing'
  });

  $('input[name=paths:list]', table).live('click', function(e){
    if(e.target.type=='radio'){
      table.ftwtable('param', 'path', e.target.value);
      table.ftwtable('param', 'show', 'tasks');
      table.ftwtable('reload');
      $('.wizard li.selected').removeClass(
        'selected').addClass('visited').next().addClass('selected');
      $('#form-controls input[name=save]').toggle();
    }
  });

  $('.wizard a[href$=#templates]').click(function(e){
    table.ftwtable('param', 'path', '/');
    table.ftwtable('param', 'show', 'templates');
    table.ftwtable('reload');
    $('.wizard li.selected').removeClass('selected');
    $(e.target).closest('li').addClass('selected');
    $('#form-controls input[name=save]').toggle();
  }, false);

  $('.wizard a[href$=#tasks]').click(function(e){
    var path = table.ftwtable('param', 'path');
    if (path == '/'){
      return false;
    }
    table.ftwtable('param', 'path', path);
    table.ftwtable('param', 'show', 'tasks');
    table.ftwtable('reload');
    $('#form-controls input[name=save]').toggle();
    return true;
  }, false);

});
