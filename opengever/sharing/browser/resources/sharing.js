var sharingApp = {
  template: '#sharing-form',
  el: '#sharing-view-vue-app',
  data: {
    i18n: {},
    available_roles: [],
    entries: [],
    inherit: null,
    principal_search: null,
    isEditable: false,
    isSaving: false,
    isSearching: false,
  },

  beforeMount: function () {
    if (!this.$el.attributes['data-contexturl']){
      return;
    }

    this.context_url = this.$el.attributes['data-contexturl'].value;
    this.portal_url = this.$el.attributes['data-portalurl'].value;
    this.endpoint = this.context_url + '/@sharing';
    this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);
    this.isEditable = JSON.parse(this.$el.attributes['data-is-editable'].value);

    var requester = axios.create();
    requester.defaults.headers.common['Accept'] = 'application/json';
    requester.defaults.headers.common['Content-Type'] = 'application/json';
    this.requester = requester;
  },

  mounted: function () {
    this.fetchData();
  },

  computed: {
    messenger: MessageFactory.getInstance,
  },

  methods: {
    fetchData: function () {
      // make sure IE 11 does not cache the fetch request
      var params = { _t: Date.now().toString()};
      if (this.isEditable === false){
        params['ignore_permissions'] = 1
      }

      this.requester.get(this.endpoint, { params: params }).then(function (response) {
        this.available_roles = response.data['available_roles'];
        this.entries = response.data['entries'];
        this.inherit = response.data['inherit'];
      }.bind(this));
    },

    toggle_checkbox: function (event, entry, role) {
      // Handler which is called when a checkbox gets changed (checked or unchecked)
      var checkbox = event.target;
      entry.roles[role] = checkbox.checked;

      // Mark entry as changed, by setting disabled to false, so it
      // gets not replaced when searching for other principal
      entry.disabled = false;
    },

    toggle_assignments: function (entry) {
      if (!entry.assignments){
        var params = { _t: Date.now().toString()};
        var url = this.context_url + '/@role-assignments/' + entry.id;
        this.requester.get(url, params).then(function (response) {
          Vue.set(entry, 'assignments', response.data);
        }.bind(this));
      }
      else {
        entry.assignments = null;
      }
    },

    highlight_roles: function (event, entry, assignment) {
      assignment.roles.forEach(function(role) {
        entry.automatic_roles[role] = 'highlight';
      });
    },

    unhighlight_roles: function (event, entry, assignment) {
      assignment.roles.forEach(function(role) {
        entry.automatic_roles[role] = true;
      });
    },

    show_info_assignment_button: function (entry) {
      return Object.keys(entry.automatic_roles)
        .map(function(key) { return entry.automatic_roles[key]; })
        .reduce(function(a, b) {
          return a || b;
        }, false);
    },

    search: function() {
      this.isSearching = true;

      // make sure IE 11 does not cache the fetch request
      var params = { _t: Date.now().toString(), search: this.principal_search };
      if (this.isEditable === false){
        params['ignore_permissions'] = 1
      }

      this.requester.get(this.endpoint, { params: params }).then(function (response) {

        // Drop former search results, which has not been changed.
        this.entries = this.entries.filter(function(i) { return i.disabled === false; });

        var current_ids = this.entries.map( function(i) { return i.id})
        this.entries = this.entries.concat(
          response.data['entries'].filter(function(i) {
            return i.disabled !== false && current_ids.indexOf(i.id) === -1;
          }));
        this.inherit = response.data['inherit'];

        this.isSearching = false;
      }.bind(this));
    },

    save: function(event){
      this.isSaving = true

      payload = {
        entries: this.entries,
        inherit: this.inherit };

      this.requester.post(this.endpoint, payload)
        .then(function (response) {
          window.location = this.context_url + '/sharing/saved';
        }.bind(this))
        .catch(function(error){
          this.messenger.shout(
            [{'messageTitle': this.i18n.message_title_error,
              'message': this.i18n.label_save_failed, 'messageClass': 'error'}]);
          this.isSaving = false
        }.bind(this));
    },
  },
};

function initSharingApp() { return new Vue(sharingApp); }

$(document).on('reload', function() {
  if (window.tabbedview) {
    var viewName = window.tabbedview.prop('view_name');
    if (viewName && viewName === 'sharing') {
      initSharingApp();
    }
  }
});

$(function() {
  if (document.querySelector('.template-sharing')) {
    initSharingApp();
  }
});
