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

  function ConfigItem(data) {
    this.id = data.id;
    this.title = data.title;
    this.help_text = data.help_text;
    this.value = data.value;
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
    var configurations;
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

      if (configurations) {
        // Rendering after update
        data.configurations.forEach(function(config_item) {
          if (!configurations[config_item.id].changed) {
            configurations[config_item.id] = new ConfigItem(config_item);
          }
        });
      } else {
        // Initial rendering
        configurations = {};
        data.configurations.forEach(function(config_item) {
          configurations[config_item.id] = new ConfigItem(config_item);
        });
      }

      var values = Object.keys(activities).map(function(e) { return activities[e]});

      var tabs = [
        {tabId: 'general',
         tabTitle: this.getDataAttribute('tab-title-general'),
         configurations: configurations,
         activities: this.filterActivitiesByType(values, 'watcher')},
        {tabId: 'tasks',
         tabTitle: this.getDataAttribute('tab-title-task'),
         activities: this.filterActivitiesByType(values, 'task')},
        {tabId: 'dossiers',
         tabTitle: this.getDataAttribute('tab-title-dossiers'),
         activities: this.filterActivitiesByType(values, 'dossier')},
        {tabId: 'reminders',
         tabTitle: this.getDataAttribute('tab-title-reminders'),
         activities: this.filterActivitiesByType(values, 'reminder')},
      ];
      if (this.getDataAttribute('show-workspaces') == 'True') {
        tabs.push({tabId: 'workspaces',
           tabTitle: this.getDataAttribute('tab-title-workspaces'),
           activities: this.filterActivitiesByType(values, 'workspace')
        });
      }
      if (this.getDataAttribute('show-proposals') == 'True') {
        tabs.push({tabId: 'proposals',
           tabTitle: this.getDataAttribute('tab-title-proposals'),
           activities: this.filterActivitiesByType(values, 'proposal')
        });
      }
      if (this.getDataAttribute('show-disposition') == 'True') {
        tabs.push({tabId: 'dispositions',
           tabTitle: this.getDataAttribute('tab-title-dispositions'),
           activities: this.filterActivitiesByType(values, 'disposition')
        });
      }
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

    this.save_config = function(target, event) {
      var checkbox = target.siblings('input:checkbox')[0];
      return this.request($('#notification-settings-form').data('save-user-setting-url'), {
        method: "POST",
        data: { config_name: checkbox.value,
                value: checkbox.checked}
      }).done(function() {
        configurations[checkbox.value].changed = false;
      });
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

    this.reset_config= function(target, event){
      var checkbox = target.siblings('input:checkbox')[0];
      return this.request($('#notification-settings-form').data('reset-user-setting-url'), {
        method: "POST",
        data: { config_name: checkbox.value}
      }).done(function() {
        configurations[checkbox.value].changed = false;
      });
    };

    this.cancel_setting = function(target, event){
      var row = target.parents('tr');
      activities[row.data('kind')].changed = false;
    };

    this.cancel_config = function(target, event){
      var checkbox = target.siblings('input:checkbox')[0];
      configurations[checkbox.value].changed = false;
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

    this.track_config_changes = function(target) {
      var config = configurations[target.context.value];
      config.changed = true;
      config.value = target.prop('checked');
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
        target: ".save-config",
        callback: this.save_config,
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
        target: ".reset-config",
        callback: this.reset_config,
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
        method: "click",
        target: ".cancel-config",
        callback: this.cancel_config,
        options: {
          update: true
        }
      },
      {
        method: "change",
        target: ".settings-trigger",
        callback: this.track_settings_changes
      },

      {
        method: "change",
        target: ".config-trigger",
        callback: this.track_config_changes
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
