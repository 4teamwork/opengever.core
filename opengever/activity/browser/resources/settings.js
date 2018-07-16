(function(global, $, Controller, HBS) {

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
    this.digest = data.digest;
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
    var currentTab = 0;

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

      var values = Object.keys(activities).map(function(e) { return activities[e]});

      var tabs = [
        {tabId: 'tasks',
         tabTitle: this.getDataAttribute('tab-title-task'),
         activities: this.filterActivitiesByType(values, 'task')},
        {tabId: 'forwardings',
         tabTitle: this.getDataAttribute('tab-title-forwardings'),
         activities: this.filterActivitiesByType(values, 'forwarding')},
        {tabId: 'proposals',
         tabTitle: this.getDataAttribute('tab-title-proposals'),
         activities: this.filterActivitiesByType(values, 'proposal')},
        {tabId: 'reminders',
         tabTitle: this.getDataAttribute('tab-title-reminders'),
         activities: this.filterActivitiesByType(values, 'reminder')},
      ];

      return this.template({
        tabs: tabs,
        translations: data.translations,
      });
    };

    this.filterActivitiesByType = function(activities, typeId) {
      return activities.filter(function(a) { return a.type_id === typeId})
    };

    this.getDataAttribute = function(id) {
      return $('#notification-settings-form').data(id);
    };

    this.initTabs = function() {
      $('ul.formTabs').tabs('.panes > div', {
        current: 'selected',
        initialIndex: currentTab,
        onBeforeClick: function(event, index) {
          currentTab = index}});
    };

    this.onRender = function() {
      this.initTabs();
    };

    this.save_setting = function(target, event) {
      var row = target.parents('tr');
      var mail = row.find("ul.mail input:checkbox:checked").map(function(){ return $(this).val(); }).get();
      var badge = row.find("ul.badge input:checkbox:checked").map(function(){ return $(this).val(); }).get();
      var digest = row.find("ul.digest input:checkbox:checked").map(function(){ return $(this).val(); }).get();

      return this.request($('#notification-settings-form').data('save-url'), {
        method: "POST",
        data: { kind: row.data('kind'),
                mail: JSON.stringify(mail),
                badge: JSON.stringify(badge),
                digest: JSON.stringify(digest)}
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

    this.refresh = function() {
      this.outlet.html(this.render(this.cache));
      this.initTabs();
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

}(window, window.jQuery, window.Controller, window.Handlebars));
