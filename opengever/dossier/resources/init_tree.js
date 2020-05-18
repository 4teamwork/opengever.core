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
    if (tree_data.length === 0 ) {
      $('#dossier-tree').hide();
      $('#dossier-tree-empty').show();
      return;
    }
    var navtree = make_tree(tree_data, {
      components: [new BusinessCaseDossierIconLinks()],
      expandActive: true
    });
    var tree_root = tree_container.find('>ul');

    tree_root.html('');
    navtree.render(tree_root);
    navtree.selectCurrent(find_parent_node_for_url(
              navtree, tree_container.data('context-url')));
  };

  BusinessCaseDossierIconLinks = function() {
    var self = {
      listen: function(tree) {
        $(tree).bind('tree:link-created', function(event, node, link) {
          link.addClass('contenttype-opengever-dossier-businesscasedossier');
        });
      }
    };
    return self;
  }

  $.ajax({
    dataType: 'json',
    url: tree_container.data('dossier-navigation-url'),
    cache: false,
    success: function(data) {
      render_tree(data);
    }
  });
});
