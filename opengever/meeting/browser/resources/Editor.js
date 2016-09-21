(function($, HBS, Controller, MeetingStorage, Synchronizer) {

  "use strict";

  var root = $(document);

  var trixEditorTemplate = HBS.compile('<trix-editor input="{{id}}" {{#if autofocus}}autofocus{{/if}} toolbar="{{toolbar}}"></trix-editor>');

  /*
    The editor represents a trix instance in the DOM
    including the toolbar as an internal reference.
   */
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

    /*
      Save the current editor state.
      Pushes the state directly to the storage.
     */
    function save() {
      root.trigger("editor.save", [reveal.proposal, reveal.section, reveal.content]);
      storage.save(reveal.proposal, reveal.section, reveal.content);
    }

    /*
      Enable the editor and its toolbar
     */
    function enable() {
      enabled = true;
      toolbar.enable();
    }

    /*
      Disable the editor and its toolbar
     */
    function disable() {
      enabled = false;
      toolbar.disable();
    }

    reveal.save = save;
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

  /*
    Represents a trix-toolbar in the DOM.
   */
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

  /*
    Represents an editor container or proxy in the DOM.
    The EditorProxy shows the content of the corresponding editor
    but has no ability to edit this content.
    The EditorProxy can then be replaced by an editor to activate
    the editing and vice versa.
   */
  function EditorProxy(proxyElement) {
    var reveal = {};
    var id = proxyElement.data("editor-id");
    var autofocus = proxyElement.data("autofocus");
    var editor = Editor(id, { autofocus: autofocus });
    proxyElement.data("proxy", reveal);

    /*
      Replace the current proxy with the corresponding editor.
     */
    function revive() {
      editor.element.insertAfter(proxyElement);
      proxyElement.detach();
    }

    /*
      Replace the editor with the corresponding proxy.
     */
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

  /*
    This controller interacts with the UI to manage
    the events for creating and deleting Editors on demand.
   */
  function EditorController(options) {

    Controller.call(this);

    this.activeProxy;

    /*
      Create a proxy for each proposal.
     */
    this.createProxies = function() {
      $(options.target).each(function(idx, proxyElement) { EditorProxy($(proxyElement)); });
    };

    /*
      Enable the editor when the corresponding trix instance
      has been initialized and put the cursor at the end of the text.
     */
    this.enableEditor = function(target) {
      var editor = target.data("editor");
      editor.enable();
      var length = editor.editor.getDocument().toString().length;
      editor.editor.setSelectedRange(length - 1);
    };

    /*
      Replace the current proxy with an editor.
     */
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
