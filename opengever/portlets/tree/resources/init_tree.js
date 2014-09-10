$(function() {
  var portlet = $('.portlet.portletTreePortlet');
  if(!portlet) {
    return;
  }

  var navigation_json = new LocalStorageJSONCache(
      'navigation', portlet.data('navigation-url'));
  var favorites_store = new RepositoryFavorites(
      portlet.data('favorites-url'),
      portlet.data('favorites-cache-param'));

  portlet.find('#tree-complete').bind('portlet-tab:open', function() {
    if ($(this).data('initialized')) {return;} $(this).data('initialized', 'true');

    var tree_node = $(this).find('>ul');
    navigation_json.load(
        function(tree_data) {
          var expand_store = ExpandStore('expanded_uids', 'uid');
          var navtree = make_tree(tree_data, {
            render_condition: function() {
              return this.depth === 0 || expand_store.is_expanded(this.parent);
            },
            onclick: function(node, event) {
              expand_store.expand(node);
            },
            components: [expand_store, favorites_store]
          });
          tree_node.html('');
          navtree.render(tree_node);
          navtree.selectCurrent(find_parent_node_for_path(
              navtree, portlet.data('context-path')));
        });
  });

  portlet.find('#tree-favorites').bind('portlet-tab:open', function() {
    var tree_node = $(this).find('>ul');
    navigation_json.load(function(tree_data) {
      favorites_store.load(function(favorites) {
        var favorite_nodes = make_tree(tree_data).clone_by_uids(favorites);
        var navtree = make_tree(favorite_nodes, {
          render_condition: function() {
            return this.depth === 0;
          }
        });
        tree_node.html('');
        navtree.render(tree_node);
        navtree.selectCurrent(find_parent_node_for_path(
            navtree, portlet.data('context-path')));
      });
    });
  });


  portlet.find('.portlet-header-tabs').tabs(
      '.portlet-tabs > div', {
        current: 'active',
        tabs: 'li > a',
        initialIndex: parseInt($.cookie('tree-portlet-tab-index'), 10) || 0,
        onBeforeClick: function(event, index) {
          $.cookie('tree-portlet-tab-index', index.toString(), {path: '/'});
          $(this.getPanes()[index]).trigger('portlet-tab:open');
        }});

  portlet.find('.portlet-tabs > div').bind('portlet-tab:loaded', function() {
    resize_treeportlet_height();
    scroll_to_selected_item(portlet.find('.portlet-tabs'));
  });



  function find_parent_node_for_path(tree, path) {
    if (!path) {
      return null;
    }

    var node = tree.findBy({'path': path});
    if (node) {
      return node;
    }
    return find_parent_node_for_path(tree, path.slice(0, path.lastIndexOf('/')));
  }

  function resize_treeportlet_height() {
    $('dl.portlet.portletTreePortlet .portlet-tabs').css(
        'height',
        $(window).height() - $('dl.portlet.portletTreePortlet .portlet-tabs').
          offset().top +'px');
  }
  $(window).resize(resize_treeportlet_height);

  function scroll_to_selected_item(tree) {
    var position = tree.find('a.current').position();
    if (position) {
      $('.portletTreePortlet dd.portletItem').scrollTop(position.top - 60);
    }
  }
});
