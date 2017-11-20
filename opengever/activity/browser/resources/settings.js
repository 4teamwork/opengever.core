(function(global, $, Controller, EditboxController, Pin, HBS) {

  "use strict";

  HBS.registerHelper({
    or: function (v1, v2) {return v1 || v2;}
  });

  HBS.registerHelper('equals', function(arg1, arg2, options) {
    return (arg1 === arg2) ? options.fn(this) : options.inverse(this);
  });

  HBS.registerHelper('translate', function(messageString, options) {
    return options.data.root.translations[messageString];
  });

  function SettingRow(data) {
    this.kind = data.kind;
    this.type_id = data.type_id;
    this.kind_title = data.kind_title;
    this.css_class = data.css_class;
    this.mail = data.mail;
    this.badge = data.badge;
    this.setting_type = data.setting_type;
    this.changed = false;
  }


  function SettingsFormController(options) {
    global.Controller.call(
      this,
      $('#settingsForm').html(),
      $('#notification-settings-form'));

    this.fetch = function(){
      return $.get($('#notification-settings-form').data('list-url'));
    };

    var activities;

    this.render = function(data) {
      if (activities) {
        // Rendering after update
        data.activities.forEach(function(activity) {
          if (!activities[activity.kind].changed) {
            activities[activity.kind] = new SettingRow(activity);
          }
        });
      } else {
        // Initial rendering
        activities = {};

        data.activities.forEach(function(activity) {
          activities[activity.kind] = new SettingRow(activity);
        });
      }
      return this.template({ activities: Object.values(activities), translations: data.translations });
    };

    this.save_setting = function(target, event) {
      var row = target.parents('tr');
      var mail = row.find("ul.mail input:checkbox:checked").map(function(){ return $(this).val(); }).get();
      var badge = row.find("ul.badge input:checkbox:checked").map(function(){ return $(this).val(); }).get();

      return this.request($('#notification-settings-form').data('save-url'), {
        method: "POST",
        data: { kind: row.data('kind'),
                mail: JSON.stringify(mail),
                badge: JSON.stringify(badge)}
      }).done(function() {
        activities[row.data('kind')].changed = false;
      });
    };

    this.reset_setting = function(target, event){
      var row = target.parents('tr');
      var kind = row.data('kind');
      return this.request($('#notification-settings-form').data('reset-url'), {
        method: "POST", data: {kind: kind}
      }).done(function(){
        activities[row.data('kind')].changed = false;
      });
    };

    this.cancel_setting = function(target, event){
      var row = target.parents('tr');
      activities[row.data('kind')].changed = false;
    };


    this.track_settings_changes = function(target) {
      var row = activities[target.parents('tr').data().kind];

      row.changed = true;
      var name = target.attr('name');
      var value = target.val();

      row[name][value] = target.prop('checked');
      this.refresh();
    };

    this.events = [
      {
        method: "click",
        target: ".save-setting",
        callback: this.save_setting,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".reset-setting",
        callback: this.reset_setting,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".cancel-setting",
        callback: this.cancel_setting,
        options: {
          update: true
        }
      },

      {
        method: "change",
        target: ".settings-trigger",
        callback: this.track_settings_changes
      }
    ];

    this.init();

  }

  $(function() {

    if($("#notification-settings-form").length) {
      var settingsFormController = new SettingsFormController();
    }

  });

}(window, window.jQuery, window.Controller, window.EditboxController, window.Pin, window.Handlebars));
