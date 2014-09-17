$(function() {
  var portlet = $('.portlet.portletTreePortlet');
  if(!portlet) {
    return;
  }

  $(document).bind('tree:rendered', function() {
    resize_treeportlet_height();
    scroll_to_selected_item(portlet.find('.portlet-tabs'));
  });


  var navigation_json = new LocalStorageJSONCache(
      'navigation', portlet.data('navigation-url'));
  var favorites_store = new RepositoryFavorites(
      portlet.data('favorites-url'),
      portlet.data('favorites-cache-param'));

  /* Complete tree tab */
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

  /* Favorites tree tab */
  var favorites_tree;
  function render_favorites_tree() {
    var tree_node = portlet.find('#tree-favorites').find('>ul');
    var expanded_uids = [];
    if(favorites_tree) {
      expanded_uids = favorites_tree.dump_expanded_uids();
    }

    navigation_json.load(function(tree_data) {
      favorites_store.load(function(favorites) {
        var favorite_nodes = make_tree(tree_data).clone_by_uids(favorites);
        sort_by_text(favorite_nodes);
        favorites_tree = make_tree(favorite_nodes, {
          render_condition: function() {
            return this.depth === 0;
          },
          components: [favorites_store]
        });
        tree_node.html('');
        favorites_tree.render(tree_node);
        favorites_tree.selectCurrent(find_parent_node_for_path(
            favorites_tree, portlet.data('context-path')));
        favorites_tree.load_expanded_uids(expanded_uids);
      });
    });
  }

  portlet.find('#tree-favorites').bind('portlet-tab:open', render_favorites_tree);

  $(favorites_store).bind('favorites:changed', function() {
    if(portlet.find('#tree-favorites').is(':visible')) {
      render_favorites_tree();
    }
  });


  /* Tabs configuration */
  portlet.find('.portlet-header-tabs').tabs(
      '.portlet-tabs > div', {
        current: 'active',
        tabs: 'li > a',
        initialIndex: parseInt($.cookie('tree-portlet-tab-index'), 10) || 0,
        onBeforeClick: function(event, index) {
          $.cookie('tree-portlet-tab-index', index.toString(), {path: '/'});
          $(this.getPanes()[index]).trigger('portlet-tab:open');
        }});


  /* Helpers */

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
    var tabs = $('dl.portlet.portletTreePortlet .portlet-tabs');
    var max = $(window).height() - tabs.offset().top - 20;
    tabs.css('max-height', max);
  }
  $(window).resize(resize_treeportlet_height);

  function scroll_to_selected_item(tree) {
    var position = tree.find('a.current').position();
    if (position) {
      $('.portletTreePortlet dd.portletItem').scrollTop(position.top - 60);
    }
  }

  function sort_by_text(list_of_nodes) {
    /* Sorts a list of nodes by text in-place. */
    function compare_text(first, second) {
      var a = first.text;
      var b = second.text;
      if (a < b) {
        return -1;
      }
      else if (a > b) {
        return 1;
      }
      else {
        return 0;
      }
    }
    list_of_nodes.sort(compare_text);
  }
});
