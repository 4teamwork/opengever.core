(function(global, $) {

  "use strict";

  function BaseContactController(template, outlet, options, addFormTemplate) {

    global.Controller.call(this, template, outlet, options);

    var self = this;

    this.new_row = Handlebars.compile(addFormTemplate);

    this.editEnabled = false;

    // TODO: To be able to override the event-functions
    // in a subcalss, I have do call it like below...
    // is there no other way to do that?
    this._showEditForm = function(target) {
      this.showEditForm(target);
    };

    this.showEditForm = function(target) {
      this.editEnabled = true;
    };

    this._abortEditForm = function(target) {
      this.abortEditForm(target);
    };

    this.abortEditForm = function(target) {
      this.editEnabled = false;
    };

    this._saveEditForm = function(target) {
      this.saveEditForm(target);
    };

    this.saveEditForm = $.noop;

    this._removeRow = function(target) {
      this.removeRow(target);
    }

    this.removeRow = function(target) {
      target.parent('.editableRow').remove();
    }

    this._addRow = function(target) {
      this.addRow(target);
    }

    this.addRow = function(target) {
      $(this.new_row()).insertAfter($('.editableRow', target.parent()).last())
    }

    this.events = [
      {
        method: "click",
        target: ".show-edit-form",
        callback: this._showEditForm,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".save-edit-form",
        callback: this._saveEditForm,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".abort-edit-form",
        callback: this._abortEditForm,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".remove-row",
        callback: this._removeRow,
      },
      {
        method: "click",
        target: ".add-row",
        callback: this._addRow,
      },

    ];

  }

  function MailContactController(options) {

    BaseContactController.call(
      this,
      $('#emailTemplate').html(),
      $('#mail-form'),
      options,
      $('#email-edit-row', this.outlet).html());

    var self = this;

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

    this.saveEditForm = function(target) {
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

    this.fetch = function() { return $.get(this.outlet.data('fetch-url')); };

    this.render = function(data) {
      return this.template({ mailaddresses: data.mailaddresses, editEnabled: this.editEnabled }); };

    this.events = this.events.concat([]);

    this.init();

  }

  $(function() {

    Handlebars.registerPartial("form-toggler-partial", $("#form-toggler-partial").html());
    Handlebars.registerPartial("email-edit-row", $("#email-edit-row").html());

    if ($(".portaltype-opengever-contact-person.template-view").length) {
      var mailContactController = new MailContactController();
    }

  });

}(window, jQuery));
