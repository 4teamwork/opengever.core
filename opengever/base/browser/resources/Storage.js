(function(global, $, MessageFactory) {

  "use strict";

  function Storage(options) {

    this.options = $.extend({ root: "storage" }, options || {});

    Storage.storage = null;

    var messageFactory = global.MessageFactory.getInstance();

    this.data = {};

    var isSupported = function() { return typeof global.localStorage !== "undefined"; };

    this.push = function() {
      try {
        Storage.storage.setItem(this.options.root, JSON.stringify(this.data) || {});
      } catch (storageError) {
        messageFactory.shout([{ messageTitle: "Error", messageClass: "error", message: storageError }]);
      }
    };

    this.pull = function() {
      this.data = JSON.parse(Storage.storage.getItem(this.options.root), this.reviver) || {};
      this.postPull();
    };

    this.drop = function() { Storage.storage.removeItem(this.options.root); };

    this.reviver = $.noop;

    this.postPull = $.noop;

    if (!isSupported()) {
      throw new Error("LocalStroage is not supported");
    } else {
      Storage.storage = window.localStorage;
    }

  }


  }


}(window, jQuery, window.MessageFactory));
