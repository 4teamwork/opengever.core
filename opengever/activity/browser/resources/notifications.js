$(function(){
  var viewlet = $('#portal-notifications dl.notificationsMenu');

  $('#portal-notifications a.mark_as_read').live('click', function(e){
    e.preventDefault();
    notification_item = $(this).parents('li.notification-item');
    mark_as_read(notification_item);
  });

  function mark_as_read(item){
    $.ajax({
      type: 'POST',
      url: viewlet.data('read-url'),
      data: {'notification_id': $(item).data('notification-id')},
      success: function(data) {
        update_unread_counter(-1);
        $(item).hide();
      }
    });
  }

  function update_unread_counter(value){
    unread_counter = $('dl.notificationsMenu .unread_number');
    unread_number = parseInt(unread_counter.text());
    unread_number += value;
    unread_counter.html(unread_number);
    if (unread_number < 1){
      unread_counter.hide();
    }
  }
});
