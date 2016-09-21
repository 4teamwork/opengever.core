(function(global, $, MessageFactory) {

  "use strict";

  /*
    The GEVERStorage is an abstraction for the browsers
    local storage.
    It provides a way to manage a datastructure through a given
    endpoint - object in the browsers localStorage.

    options:
      - root: Set the endpoint on the localStorage
   */
  function GEVERStorage(options) {

    options = $.extend({ root: "storage" }, options);
    var messageFactory = MessageFactory.getInstance();
    var reveal = {};
    var data = {};
    var storage;

    /*
      Checks if the browser supports localStorage
     */
    function isSupported() { return typeof localStorage !== "undefined"; }

    /*
      Push the current datastructe to the localStorage by serializing
      the object.
      If something went wrong a message appears using the messageFactory
     */
    function push() {
      try {
        storage.setItem(options.root, JSON.stringify(reveal.data) || {});
      } catch (storageError) {
        messageFactory.shout([{ messageTitle: "Error", messageClass: "error", message: storageError }]);
      }
    }

    /*
      Load the data from the localStorage by parsing the JSON.
     */
    function pull() { reveal.data = JSON.parse(storage.getItem(options.root)) || {}; }

    /*
      Drop all the data from the localStorage.
     */
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
