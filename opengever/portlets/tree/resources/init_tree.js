$(function() {
  var filetree = $('.filetree');
  if (filetree.length) {
    var root_path = filetree.data()['root_path'];

    filetree.load('./tree',{'root_path': root_path}, function(){
      var tree = filetree.treeview({
        collapsed: true,
        animated: "fast",
        persist: "cookie",
        cookieId: "opengever-treeview"
      });
      resize_treeportlet_height();
      scroll_to_selected_item(filetree);
    });

    $(window).resize(function() {
      resize_treeportlet_height();
    });

  }

});

function resize_treeportlet_height() {
  $('dl.portlet.portletTreePortlet').css(
    'height',
    $(window).height() - $('dl.portlet.portletTreePortlet').offset().top +'px')
}

function scroll_to_selected_item(tree) {
  var position = tree.find('a.selected').position();
  if (position) {
    $('.portletTreePortlet dd.portletItem').scrollTop(position.top - 60);
  }
}
