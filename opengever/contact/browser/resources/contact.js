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

    var self = this;

    var protocolSynchronizer = new global.Synchronizer(
      { target: "#mail-form input", triggers: ["input"] });

    protocolSynchronizer.observe();
    protocolSynchronizer.onSync(function(target){
      $('.save-edit-form').addClass('disabled');
      var row = target.closest('li');

      self.request(self.outlet.data('validate-url'), {
        data: {label: $('input[name="label"]', row).val(),
               address: $('input[name="email"]', row).val()}
      }).fail(function(data){
        $(row).addClass('error');
        $(row).children('.validation-error').html(data.messages[0].message);
      }).done(function(){
        $('.save-edit-form').removeClass('disabled');
        $(row).children('.validation-error').html('')
        $(row).removeClass('error');
      })
    });

    BaseContactController.call(
      this,
      $('#emailTemplate').html(),
      $('#mail-form'),
      options,
      $('#email-edit-row', this.outlet).html());

    this.saveEditForm = function(target) {
      var rows = $('.editableRow', this.outlet);
      var self = this;
      var data = []

      rows.each(function(e) {
        data.push({id: $(this).data('id'),
                   method: $(this).data('action'),
                   values: {label: $('input[name="label"]', this).val(),
                            address: $('input[name="email"]', this).val()}
                  });
      });

      self.request(self.outlet.data('set_all-url'), {
        method: "POST",
        data: {'objects': JSON.stringify(data)},
      })

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
