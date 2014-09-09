$(function() {
  var expand_store = ExpandStore('expanded_uids', 'uid');
  var filetree = $('.filetree');
  var navtree;

  if (!filetree.length) {
    return;
  }

  var root_path = filetree.data()['root_path'];
  var context_path = filetree.attr('data-context_path');

  json_cache = new LocalStorageJSONCache('navigation');
  json_cache.load(
      $('.portletTreePortlet').data('navigation-url'),
      function(tree_data) {
        $('dl.portletTreePortlet ul.filetree').html('');
        navtree = make_tree(tree_data, {
          render_condition: function() {
            return this.depth === 0 || expand_store.is_expanded(this.parent);
          },
          onclick: function(node, event) {
            expand_store.expand(node);
          }
        });
        navtree.render('dl.portletTreePortlet ul.filetree');
        navtree.selectCurrent(find_parent_node_for_path(context_path));
        resize_treeportlet_height();
        scroll_to_selected_item(filetree);
      });

  $('ul.filetree a.toggleNav').live('click', function(e){
    e.preventDefault();
    var arrow = $(this);
    var link = arrow.siblings('a');
    var node = link.data('tree-node');

    if(navtree.is_expanded(node)) {
      navtree.collapse(node);
      expand_store.collapse(node);
    } else {
      navtree.expand(node);
      expand_store.expand(node);
    }
  });

  $(window).resize(function() {
    resize_treeportlet_height();
  });

  function find_parent_node_for_path(path) {
    if (!path) {
      return null;
    }

    var node = navtree.findBy({'path': path});
    if (node) {
      return node;
    }
    return find_parent_node_for_path(path.slice(0, path.lastIndexOf('/')));
  }

  function resize_treeportlet_height() {
    $('dl.portlet.portletTreePortlet').css(
      'height',
      $(window).height() - $('dl.portlet.portletTreePortlet').offset().top +'px');
  }

  function scroll_to_selected_item(tree) {
    var position = tree.find('a.inPath:last').position();
    if (position) {
      $('.portletTreePortlet dd.portletItem').scrollTop(position.top - 60);
    }
  }
});
