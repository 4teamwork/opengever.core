$(function() {
 var root_path = $('.filetree').data()['root_path'];

  $('.filetree').load('./tree',{'root_path': root_path}, function(){
    var tree = $(".filetree").treeview({
      collapsed: true,
      animated: "fast",
      persist: "cookie",
      cookieId: "opengever-treeview"
    });
  });

});
