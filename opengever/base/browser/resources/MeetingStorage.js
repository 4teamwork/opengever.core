(function(global, $, GEVERStorage) {

  "use strict";

  /*
    The MeetingStorage provides a singleton which refers to a
    GEVERStorage instance always pointing to the same
    endpoint - protocol in that case.
    The MeetingStorage augments the abstract GEVERStorage for
    saving, getting or deleting a meeting.

    ! Each operation has direct impact on the localStorage
      So there is no transaction mechanism. !
   */

  var MeetingStorage = (function MeetingStorage() {
    var storage;

    /*
      Get the current meeting provided by the backend out of the DOM
     */
    function currentMeeting() { return $(".protocol-navigation").data("meeting"); }

    /*
      Save a new proposal on the current meeting
      providing a proposalId, a section and the content.
     */
    function save(proposal, section, data) {
      var meeting = currentMeeting();
      storage.data[meeting] = storage.data[meeting] || {};
      storage.data[meeting].revision = new Date().getTime();
      storage.data[meeting][proposal] = storage.data[meeting][proposal] || {};
      storage.data[meeting][proposal][section] = storage.data[meeting][proposal][section] || {};
      storage.data[meeting][proposal][section] = data;
      storage.push();
    }

    /*
      Destroy a meeting.
      If no meeting is set the current meeting will
      be destroyed.
     */
    function destroy(meeting) {
      meeting = meeting || currentMeeting();
      delete storage.data[meeting];
      storage.push();
    }

    /*
      Get a meeting by passing a meetingId.
      If no meeting is set the current meeting will
      be returned.
     */
    function get(meeting) {
      meeting = meeting || currentMeeting();
      return storage.data[meeting] || {};
    }

    /*
      Internal function for setting up the
      GEVERStorage augmentation.
      Triggers an initial pull of the storage.
     */
    function init() {
      storage = GEVERStorage({ root: "protocol" });
      storage.save = save;
      storage.destroy = destroy;
      storage.get = get;
      storage.pull();
    }

    /*
      Returns a singleton instance of the MeetingStorage
     */
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
