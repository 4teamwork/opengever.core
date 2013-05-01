$(function(){

  // initially hide the save button
  $('#form-controls input[name=save]').hide();

  //test global overwrite
  $.fn.ftwtable.defaults.onBeforeLoad = function(){
  };

  // initialize table
  table = $('#template_chooser').ftwtable({
    'url' : '@@add-tasktemplate/listing'
  });

  // reset when clicking on first wizard step label
  $('.wizard a[href$=#templates]').click(function(e){
    table.ftwtable('param', 'path', '/');
    table.ftwtable('param', 'show', 'templates');
    table.ftwtable('reload');
    $('.wizard li.selected').removeClass('selected');
    $(e.target).closest('li').addClass('selected');
    $('#form-controls input[name=save]').hide();
    $('#form-controls input[name=continue]').show();
  }, false);

  // continue button moves from "templates" step to "tasks" step
  $('#form-controls input[name=continue]').live('click', function(e) {
    e.preventDefault();
    var radio = $('input[name=paths:list]:checked:first');
    if(radio.length==1) {
      table.ftwtable('param', 'path', radio.attr('value'));
      table.ftwtable('param', 'show', 'tasks');
      table.ftwtable('reload');
      $('.wizard li.selected').removeClass(
        'selected').addClass('visited').next().addClass('selected');
      $('#form-controls input[name=save]').show();
      $('#form-controls input[name=continue]').hide();
    }
  });

  $('.wizard a[href$=#tasks]').click(function(e){
    var path = table.ftwtable('param', 'path');
    if (path == '/'){
      return false;
    }
    table.ftwtable('param', 'path', path);
    table.ftwtable('param', 'show', 'tasks');
    table.ftwtable('reload');
    $('#form-controls input[name=save]').show();
    return true;
  }, false);

});
