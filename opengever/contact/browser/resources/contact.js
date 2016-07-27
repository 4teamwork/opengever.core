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
    };

    this.removeRow = function(target) {
      var row = target.parent('.editableRow');
      row.data('action', 'remove');
      row.hide();
    };

    this._addRow = function(target) {
      this.addRow(target);
    };

    this.addRow = function(target) {

      var row = $(this.new_row());
      row.data('action', 'add');

      target.siblings('.form-list').append(row);
    };

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

    Handlebars.registerPartial("email-edit-row", $("#email-edit-row").html());

    BaseContactController.call(
      this,
      $('#emailTemplate').html(),
      $('#mail-form'),
      options,
      $('#email-edit-row', this.outlet).html());

    var self = this;

    this.saveEditForm = function(target) {
      var rows = $('.editableRow', this.outlet);
      var self = this;

      rows.each(function() {
        var mailLabel = $('input[name="label"]', this);
        var mailAddress = $('input[name="email"]', this);

        var state = $(this).data('action');

        if (state === 'update') {
          self.request($(this).data('update-url'), {
            method: "POST",
            data: {
              label: mailLabel.val(),
              mailaddress: mailAddress.val(),
            }
          });
        }

        else if (state === 'add') {
          self.request(self.outlet.data('create-url'), {
            method: "POST",
            data: {
              label: mailLabel.val(),
              mailaddress: mailAddress.val()
            }
          });
        }

        else if (state === 'remove') {
          return $.post($(this).data('delete-url'));
        }

      });

      this.editEnabled = false;
    };

    this.fetch = function() { return $.get(this.outlet.data('fetch-url')); };

    this.render = function(data) {
      return this.template({ mailaddresses: data.mailaddresses, editEnabled: this.editEnabled }); };

    this.events = this.events.concat([]);

    this.init();

  }

  $(function() {
    if ($(".portaltype-opengever-contact-person.template-view").length) {
      Handlebars.registerPartial("form-toggler-partial", $("#form-toggler-partial").html());

      var mailContactController = new MailContactController();
    }

  });

}(window, jQuery));
