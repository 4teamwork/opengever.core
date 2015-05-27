$(function() {
  var tree_container = $('#dossier-tree');

  function find_parent_node_for_url(tree, url) {
    if (!url) {
      return null;
    }

    var node = tree.findBy({'url': url});
    if (node) {
      return node;
    }
    return find_parent_node_for_url(tree, url.slice(0, url.lastIndexOf('/')));
  }

  function render_tree(tree_data) {
    navtree = make_tree(tree_data);
    tree_container.html('');
    navtree.render(tree_container);
    navtree.selectCurrent(find_parent_node_for_url(
              navtree, tree_container.data('context-url')));
  };

  $.ajax({
    dataType: 'json',
    url: tree_container.data('dossier-navigation-url'),
    cache: false,
    success: function(data) {
      render_tree(data);
    }
  });
});
