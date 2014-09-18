function make_tree(nodes, config) {
  return new Tree(nodes, config);
}

function Tree(nodes, config) {
  nodes = jQuery.extend(true, [], nodes);
  var tree_root;
  var tree = this;
  var internal_node_keys = ['parent', 'depth', 'link', 'nodes'];
  configuration = $.extend(true, {
    'render_condition': function(){ return true; },
    'onclick': function(node, event){},
    'components': []
  }, config);
  $(configuration['components']).each(function(_, component) {
    if(component !== null) {
      component.listen(tree);
    }
  });

  this.render = function(selector) {
    if(typeof(selector.jquery) === 'undefined') {
      tree_root = $(selector);
    } else {
      tree_root = selector;
    }
    var temporary_root = $('<ul/>');
    $(this.nodes()).each(function() {
      tree.render_node_into_container.apply(this, [temporary_root]);
    });
    temporary_root.find('>*').appendTo(tree_root);
    $(document).trigger('tree:rendered', [this]);
  };

  this.render_node = function() {
    if(!this.link) {
      tree.render_node.apply(this.parent);
      tree.render_children.apply(this.parent, [true]);
    }
  };

  this.render_node_into_container = function($container, force_render) {
    if(!force_render && !configuration.render_condition.apply(this)) {
      return;
    }
    var $list_item = $('<li/>');
    if (this.nodes && this.nodes.length > 0) {
      $('<a href="#" class="toggleNav">&nbsp;</a>').
          appendTo($list_item).
          click(tree.arrow_clicked);
    }
    $container.append($list_item);
    var $link = $('<a />').text(this.text).attr('href', this.path);
    $list_item.append($link);
    $(tree).trigger('tree:link-created', [this, $link]);

    for(var key in this.data) {
      $link.attr('data-'.concat(key), this.data[key]);
    }

    $link.click(function(event) {
      configuration.onclick.apply(this, [$(this).data('tree-node'), event]);
    });

    $link.data('tree-node', this);
    this['link'] = $link;
    tree.render_children.apply(this);

    if(this.parent) {
      tree.expand(this.parent, true);
    }
  };

  this.render_children = function(force_render) {
    if (!this.nodes || this.nodes.length === 0) {
      return;
    }
    var $sublist = this.link.parent('li').find('>ul');
    if ($sublist.find('>li').length > 0) {
      return;
    }

    if($sublist.length === 0) {
      $sublist = $('<ul class="folded" />');
      this['link'].parent('li:first').append($sublist);
    }

    $(this.nodes).each(function() {
      if (!this['link']) {
        tree.render_node_into_container.apply(this, [$sublist, force_render]);
      }
    });
  };

  this.nodes = function() {
    return nodes;
  };

  this.expand = function(node, omit_event) {
    if(this.is_expanded(node)) {
      return;
    }
    if(node.parent) {
      this.expand(node.parent, true);
    }
    this.render_children.apply(node, [true]);
    $(node.link).parent('li').find('>ul').removeClass('folded');
    $(node.link).parent('li').find('>a.toggleNav').addClass('expanded');
    if(!omit_event) {
      $(tree).trigger('tree:expanded', [node]);
    }
  };

  this.collapse = function(node) {
    $(node.link).parent('li').find('>ul').addClass('folded');
    $(node.link).parent('li').find('>a.toggleNav').removeClass('expanded');
    $(tree).trigger('tree:collapsed', [node]);
  };

  this.is_expanded = function(node) {
    return !$(node.link).parent('li').find('>ul').hasClass('folded');
  };

  this.dump_expanded_uids = function() {
    var uids = [];
    this.each(function() {
      if(tree.is_expanded(this)) {
        uids.push(this['uid']);
      }
    });
    return uids;
  };

  this.load_expanded_uids = function(uids) {
    $(uids).each(function(_, uid) {
      tree.eachBy({'uid': uid}, function() {
        tree.expand(this);
      });
    });
  };

  this.arrow_clicked = function(event) {
    event.preventDefault();
    var arrow = $(this);
    var link = arrow.siblings('a');
    var node = link.data('tree-node');

    if(tree.is_expanded(node)) {
      tree.collapse(node);
    } else {
      tree.expand(node);
    }
  };

  this.each = function(callback) {
    function recurse(depth, parent) {
      callback.apply(this, [depth, parent]);
      parent = this;
      $(this.nodes).each(function() {recurse.apply(this, [depth + 1, parent]);});
    }
    $(this.nodes()).each(function() {recurse.apply(this, [0, null]);});
  };

  this.eachBy = function(condition, callback) {
    this.each(function() {
      for(var name in condition) {
        if (this[name] != condition[name]) {
          return null;
        }
      }
      return callback.apply(this);
    });
  };

  this.findBy = function(condition) {
    var node = null;
    this.eachBy(condition, function() {
      node = this;
      return false;
    });
    return node;
  };

  this.selectCurrent = function(node) {
    if (!node) {
      return;
    }
    tree.render_node.apply(node);

    tree_root.find('.current').map(function() {
      $(this).removeClass('current');
    });

    node.link.addClass('current');
    node.link.parent('li:first').addClass('current');
  };

  this.clone_node = function(node) {
    if(!node){
      return node;
    }
    var clone = {};
    for (var key in node) {
      if($.inArray(key, internal_node_keys) === -1) {
        clone[key] = node[key];
      }
    }
    clone['nodes'] = $(node['nodes']).map(function(index, child) {
      return tree.clone_node(child);
    });
    return clone;
  };

  this.clone_by_uids = function(wanted_uids) {
    return $(wanted_uids).map(function(_, uid) {
      return tree.clone_node(tree.findBy({'uid': uid}));
    }).toArray();
  };

  this.each(function(depth, parent) {
    this.depth = depth;
    this.parent = parent;
  });
}


ExpandStore = function(cookie_name, identifier_key) {
  function get() {
    var cookie = $.cookie(cookie_name);
    if (!cookie) {
      return [];
    }
    return cookie.split(';');
  }

  function set(uids) {
    $.cookie(cookie_name, uids.join(';'), {path: '/'});
  }

  function identifier(node) {
    return node[identifier_key];
  }

  var store = {
    listen: function(tree) {
      $(tree).bind('tree:expanded', function(event, node) {
        store.expand(node);
      });
      $(tree).bind('tree:collapsed', function(event, node) {
        store.collapse(node);
      });
    },
    is_expanded: function(node) {
      if(!node) {
        return false;
      }
      return get().indexOf(identifier(node)) !== -1;
    },
    expand: function(node) {
      if (this.is_expanded(node)) {
        return;
      }

      var expanded = get();
      expanded.push(identifier(node));
      set(expanded);
    },
    collapse: function(node) {
      if (!this.is_expanded(node)) {
        return;
      }

      var expanded = get();
      expanded.remove(identifier(node));
      set(expanded);
    }
  };
  return store;
};


LocalStorageJSONCache = function(name, url) {
  /** The LocalStorageJSONCache stores JSON data from an AJAX request
      in the browser's localStorage until it changes.
      The URL **must** contain a cache key for invalidation as param,
      otherwise we have an infinite cache!
      **/
  var url_key = 'og-' + name + '-url';
  var data_key = 'og-' + name + '-data';
  var json_cache;
  url = handle_nocache(url);

  function is_cached(url) {
    return Modernizr.localstorage && localStorage.getItem(url_key) == url;
  }

  function set(url, data) {
    if (Modernizr.localstorage) {
      localStorage.setItem(url_key, url);
      localStorage.setItem(data_key, data);
    }
    json_cache = JSON.parse(data);
  }

  function get(url) {
    json_cache = JSON.parse(localStorage.getItem(data_key));
    return json_cache;
  }

  function handle_nocache(url) {
    /** If we do a hard refresh, a nocache parameter is added
        to the url so that we can detect it and clear our caches.
    **/
    if (url.indexOf('nocache=true') !== -1) {
      localStorage.removeItem(url_key);
      localStorage.removeItem(data_key);
      return url.replace(/[?&]nocache=true/, '');
    } else {
      return url;
    }
  }

  return {
    'load': function(callback) {
      if (json_cache) {
        callback(json_cache);
      }
      else if (is_cached(url)) {
        callback(get(url));
      } else {
        $.ajax({
          dataType: 'text',  // we want to store it in localStorage
          url: url,
          cache: true,
          success: function(data) {
            set(url, data);
            callback(get());
          }
        });
      }
    }};
};


RepositoryFavorites = function(url, cache_param) {
  var _data_cache;
  var local_storage = new LocalStorageJSONCache(
      'favorites', url + '/list?' + cache_param);

  var i18n_add = $('[data-i18n-add-to-favorites]').data('i18n-add-to-favorites') || '';
  var i18n_remove = $('[data-i18n-remove-from-favorites]').data('i18n-remove-from-favorites') || '';

  function annotate_link_title(favorite_link) {
    if(favorite_link.hasClass('bookmarked')) {
      favorite_link.attr('title', i18n_remove);
    } else {
      favorite_link.attr('title', i18n_add);
    }
  }

  var self = {
    listen: function(tree) {
      $(tree).bind('tree:link-created', function(event, node, link) {
        var favorite_link = $('<span class="favorite-icon"><!-- --></span>').
            prependTo(link).
            data('uuid', node['uid']).
            click(function(event) {
              event.preventDefault();
              if($(this).hasClass('bookmarked')) {
                $(this).removeClass('bookmarked');
                self.remove($(this).data('uuid'));
              } else {
                $(this).addClass('bookmarked');
                self.add($(this).data('uuid'));
              }
              annotate_link_title($(this));
            });

        self.load(function(favorites) {
          if($.inArray(node['uid'], favorites) > -1) {
            favorite_link.addClass('bookmarked');
          }
          annotate_link_title(favorite_link);
        });
      });
    },

    load: function(callback) {
      if(_data_cache) {
        callback(_data_cache);
      } else {
        local_storage.load(function(data) {
          _data_cache = data;
          callback(data);
        });
      }
    },

    add: function(uuid) {
      $.post(url + '/add', {uuid: uuid}, function() {
        _data_cache.push(uuid);
        $(self).trigger('favorites:changed');
      });
    },

    remove: function(uuid) {
      $.post(url + '/remove', {uuid: uuid}, function() {
        _data_cache.remove(uuid);
        $(self).trigger('favorites:changed');
      });
    }
  };
  return self;
};
