(function(global, $) {

  "use strict";

  function ContactController(options) {

    global.Controller.call(this, $('#emailTemplate').html(), $('#mail-form'), options);

    var self = this;

    var deleteDialog = $("#confirm_delete").overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    this.editEnabled = false;

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
      this.editEnabled = true;
    };

    this.saveEditForm = function(target) {
      this.editEnabled = false;
    };

    this.abortEditForm = function(target) {
      this.editEnabled = false;
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

    this.render = function(data) {
      return this.template({ mailaddresses: data.mailaddresses, editEnabled: this.editEnabled }); };

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
        target: ".toggle-edit-email.fa-pencil",
        callback: this.showEditForm,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".toggle-edit-email.fa-check",
        callback: this.saveEditForm,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".abort-edit-email",
        callback: this.abortEditForm,
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

    if ($(".portaltype-opengever-contact-person.template-view").length) {
      var contactController = new ContactController();
    }

  });

}(window, jQuery));
