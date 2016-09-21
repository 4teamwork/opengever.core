(function(global, $, GEVERStorage) {

  "use strict";

  var MeetingStorage = (function MeetingStorage() {
    var storage;

    function currentMeeting() { return $(".protocol-navigation").data("meeting"); }

    function save(proposal, section, data) {
      var meeting = currentMeeting();
      storage.data[meeting] = storage.data[meeting] || {};
      storage.data[meeting].revision = new Date().getTime();
      storage.data[meeting][proposal] = storage.data[meeting][proposal] || {};
      storage.data[meeting][proposal][section] = storage.data[meeting][proposal][section] || {};
      storage.data[meeting][proposal][section] = data;
      storage.push();
    }

    function destroy(meeting) {
      meeting = meeting || currentMeeting();
      delete storage.data[meeting];
      storage.push();
    }

    function get(meeting) {
      meeting = meeting || currentMeeting();
      return storage.data[meeting] || {};
    }

    function init() {
      storage = GEVERStorage({ root: "protocol" });
      storage.save = save;
      storage.destroy = destroy;
      storage.get = get;
      storage.pull();
    }

    function getInstance() {
      if(!storage) {
        init();
      }
      return storage;
    }

    return Object.freeze({ getInstance: getInstance });
  })();

  global.MeetingStorage = MeetingStorage;

})(window, window.jQuery, window.GEVERStorage);
