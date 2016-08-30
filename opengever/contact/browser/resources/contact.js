(function(global, $) {

  "use strict";
  function ParticipatedDossierController(options) {
    global.Controller.call(this,
                           $("#latest_participations_template").html(),
                           $("#latest_participation_listing"), options);

    this._show_all = false;

    this.fetch = function() {
      var url = $('#latest_participation_listing').data('fetch-url');
      return $.get(url, {'show_all': this._show_all});
    };

    this.render = function(data) {
      return this.template({ participations: data.participations,
                             has_more: data.has_more,
                             show_all_label: data.show_all_label});
    }

    this.show_all = function(data) {
      this._show_all = true;
      this.update();
    }

    this.events = [
      {
        method: "click",
        target: "#participation_show_all",
        callback: this.show_all
      }
    ];

    this.init();
  }

  function ContactController(options) {

    global.Controller.call(this, $('#emailTemplate').html(), $('#mails-list tbody'), options);

    var self = this;

    var deleteDialog = $("#confirm_delete").overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    this.openModal = function(target) {
      this.currentItem = target;
      deleteDialog.load(); };

    this.closeModal = function() { deleteDialog.close(); };

    this.addEmail = function(target) {
      var mailLabel = $('input#email-label');
      var mailAddress = $('input#email-mailaddress');

      return this.request(target.data('create-url'), {
        method: "POST",
        data: {
          label: mailLabel.val(),
          mailaddress: mailAddress.val()
        }
      }).done(function(data) {
        if (!data.proceed) { return; }
        mailLabel.val('');
        mailAddress.val('');
      });
    };

    this.removeEmail = function(target) {
      this.closeModal();
      return $.post(this.currentItem.data('delete-url'));
    };

    this.showEditForm = function(target) {
      var row = target.closest(".email-record");
      row.hide();
      row.next(".email-record-edit-form").show();
    };

    this.hideEditForm = function(target) {
      var row = target.closest(".email-record-edit-form");
      row.hide();
      row.prev(".email-record").show();
    };

    this.updateEmail = function(target) {
      var row = target.closest(".email-record-edit-form");
      var updateUrl = target.data("update-url");
      var mailAddress = $(".update-address", row);
      var mailLabel = $(".update-label", row);
      return this.request(updateUrl, {
        method: "POST",
        data: {
          label: mailLabel.val(),
          mailaddress: mailAddress.val(),
        }
      });
    };

    this.fetch = function() { return $.get($('#mails-list').data('fetch-url')); };

    this.render = function(data) { return this.template({ mailaddresses: data.mailaddresses }); };

    this.events = [
      {
        method: "click",
        target: ".add-email",
        callback: this.addEmail,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".remove-email",
        callback: this.openModal,
      },
      {
        method: "click",
        target: ".toggle-email-edit-form",
        callback: this.showEditForm
      },
      {
        method: "click",
        target: ".email-record-edit-form .cancel",
        callback: this.hideEditForm
      },
      {
        method: "click",
        target: ".email-record-edit-form .save",
        callback: this.updateEmail,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#confirm_delete .decline",
        callback: this.closeModal
      },
      {
        method: "click",
        target: "#confirm_delete .confirm",
        callback: this.removeEmail,
        options: {
          update: true
        }
      },
    ];

    this.init();

  }

  $(function() {

    if ($('body.portaltype-opengever-contact-organization').length ||
        $('body.portaltype-opengever-contact-person').length){
      var participatedDossierController = new ParticipatedDossierController();
    }

    if ($(".portaltype-opengever-contact-person.template-edit").length) {
      var contactController = new ContactController();
    }

  });

}(window, jQuery));
