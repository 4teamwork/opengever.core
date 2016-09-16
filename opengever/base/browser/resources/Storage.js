(function(global, $, MessageFactory) {

  "use strict";

  function GEVERStorage(options) {

    options = $.extend({ root: "storage" }, options);
    var messageFactory = MessageFactory.getInstance();
    var reveal = {};
    var data = {};
    var storage;

    function isSupported() { return typeof localStorage !== "undefined"; }

    function push() {
      try {
        storage.setItem(options.root, JSON.stringify(reveal.data) || {});
      } catch (storageError) {
        messageFactory.shout([{ messageTitle: "Error", messageClass: "error", message: storageError }]);
      }
    }

    function pull() { reveal.data = JSON.parse(storage.getItem(options.root)) || {}; }

    function drop() { storage.removeItem(options.root); }

    if (!isSupported()) {
      throw new Error("LocalStroage is not supported");
    } else {
      storage = window.localStorage;
    }

    reveal.data = data;
    reveal.push = push;
    reveal.pull = pull;
    reveal.drop = drop;

    return reveal;
  }

  global.GEVERStorage = GEVERStorage;

}(window, jQuery, window.MessageFactory));
