(function(global, $) {

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

  function Synchronizer(options) {

    this.options = $.extend({
      delay: 1000,
      target: global.document,
      trigger: "keyup"
    }, options || {});

    var self = this;

    var syncCallback = $.noop;

    var trackType = function(event) {
      global.clearTimeout(this.timeout);
      this.timeout = global.setTimeout(function() { syncCallback(event.target); }, self.options.delay);
    };

    this.observe = function() { $(this.options.target).on(this.options.trigger, trackType); };

    this.onSync = function(callback) { syncCallback = callback; };

  }

  function Meeting(proposals, revision) {

    var getTimestamp = function() { return new Date().getTime(); };

    this.proposals = proposals || {};
    this.revision = revision || 0;

    this.updateRevision = function() { this.revision = getTimestamp(); };

    this.addOrUpdateUnit = function(proposal, unit, text) {
      this.proposals[proposal] = this.proposals[proposal] || {};
      this.proposals[proposal][unit] = this.proposals[proposal][unit] || {};
      this.proposals[proposal][unit] = text;
    };

  }

  function MeetingStorage(meeting) {

    Storage.call(this, { root: "protocol" });

    var extendProposal = function(proposal, unit) { return "#agenda_item-" + proposal + "-" + unit; };

    var isMeeting = function(object) { return object.hasOwnProperty("proposals") && object.hasOwnProperty("revision"); };

    this.reviver = function(k, v) {
      if(isMeeting(v || {})) {
        return new Meeting(v.proposals, v.revision);
      } else {
        return v;
      }
    };

    this.addOrUpdateUnit = function(proposal, unit, text) {
      this.currentMeeting.addOrUpdateUnit(proposal, unit, text);
      this.currentMeeting.updateRevision();
      this.data[meeting] = this.data[meeting] || this.currentMeeting;
    };

    this.deleteCurrentMeeting = function() {
      delete this.data[meeting];
      this.push();
    };

    this.restore = function() {
      $.each(this.currentMeeting.proposals, function(proposalId, proposal) {
        $.each(proposal, function(unitName, unitText) {
          $(extendProposal(proposalId, unitName)).val(unitText);
        });
      });
    };

    this.postPull = function() { this.currentMeeting = this.data[meeting] || new Meeting(); };

  }

  window.MeetingStorage = MeetingStorage;
  window.Synchronizer = Synchronizer;

}(window, jQuery));
