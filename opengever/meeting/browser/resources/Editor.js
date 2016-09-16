(function($, HBS, Controller, MeetingStorage, Synchronizer) {

  "use strict";

  var root = $(document);

  var trixEditorTemplate = HBS.compile('<trix-editor input="{{id}}" {{#if autofocus}}autofocus{{/if}} toolbar="{{toolbar}}"></trix-editor>');

  function Toolbar(id) {

    var reveal = {};
    var element = $("#" + id + "-toolbar");

    function enable() { element.addClass("active"); }
    function disable() { element.removeClass("active"); }

    reveal.enable = enable;
    reveal.disable = disable;

    Object.defineProperty(reveal, "id", { get: function() { return id; }});
    Object.defineProperty(reveal, "element", { get: function() { return element; }});
    Object.defineProperty(reveal, "link", { get: function() { return id + "-toolbar"; }});

    return Object.freeze(reveal);

  }

  function Editor(id, options) {
    var reveal = {};
    var enabled = false;
    var storage = MeetingStorage.getInstance();
    var toolbar = Toolbar(id);

    options = $.extend({
      autofocus: true
    }, options);

    var element = $(trixEditorTemplate({
      toolbar: toolbar.link,
      autofocus: options.autofocus,
      id: id
    }));

    element.data("editor", reveal);

    function load(data) { element.editor.loadJSON(JSON.parse(data)); }

    function save() {
      root.trigger("editor.save", [reveal.proposal, reveal.section, reveal.content]);
      storage.save(reveal.proposal, reveal.section, reveal.content);
    }

    function enable() {
      enabled = true;
      toolbar.enable();
    }
    function disable() {
      enabled = false;
      toolbar.disable();
    }

    reveal.save = save;
    reveal.load = load;
    reveal.enable = enable;
    reveal.disable = disable;
    Object.defineProperty(reveal, "element", { get: function() { return element; }});
    Object.defineProperty(reveal, "editor", { get: function() { return element.get(0).editor; }});
    Object.defineProperty(reveal, "toolbar", { get: function() { return toolbar; }});
    Object.defineProperty(reveal, "enabled", { get: function() { return enabled; }});
    Object.defineProperty(reveal, "content", { get: function() { return element.val(); }});
    Object.defineProperty(reveal, "proposal", { get: function() { return id.split("-")[1]; }});
    Object.defineProperty(reveal, "section", { get: function() { return id.split("-")[2]; }});
    return Object.freeze(reveal);

  }

  function EditorProxy(proxyElement) {
    var reveal = {};
    var id = proxyElement.data("editor-id");
    var autofocus = proxyElement.data("autofocus");
    var editor = Editor(id, { autofocus: autofocus });
    proxyElement.data("proxy", reveal);

    function revive() {
      editor.element.insertAfter(proxyElement);
      proxyElement.detach();
    }

    function destroy() {
      editor.disable();
      proxyElement.html(editor.content);
      proxyElement.insertAfter(editor.element);
      editor.element.detach();
    }

    reveal.revive = revive;
    reveal.destroy = destroy;
    Object.defineProperty(reveal, "editor", { get: function() { return editor; }});
    return Object.freeze(reveal);
  }

  function EditorController(options) {

    Controller.call(this);

    this.activeProxy;

    this.createProxies = function() {
      $(options.target).each(function(idx, proxyElement) { EditorProxy($(proxyElement)); });
    };

    this.enableEditor = function(target) {
      var editor = target.data("editor");
      editor.enable();
      var length = editor.editor.getDocument().toString().length;
      editor.editor.setSelectedRange(length - 1);
    };

    this.revive = function(proxyElement) {
      var proxy = proxyElement.data("proxy");
      if(proxy.editor.enabled) {
        return false;
      }
      if(this.activeProxy) {
        this.activeProxy.destroy();
      }
      proxy.revive();
      this.activeProxy = proxy;
    };

    this.events = [
      {
        method: "click",
        target: options.target,
        callback: this.revive
      },
      {
        method: "ready",
        target: document,
        callback: this.createProxies
      },
      {
        method: "trix-initialize",
        target: "trix-editor",
        callback: this.enableEditor
      }
    ];

    this.init();

  }

  new EditorController({ target: ".trix-editor-proxy" });

  function syncEditor(target) { $(target).data("editor").save(); }

  var synchronizer = new Synchronizer({ target: "trix-editor", triggers: ["trix-change"] });
  synchronizer.observe();
  synchronizer.onSync(syncEditor);

})(window.jQuery, window.Handlebars, window.Controller, window.MeetingStorage, window.Synchronizer);
