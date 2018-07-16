var sharingApp = {
  template: '#sharing-form',
  el: '#sharing-view-vue-app',
  data: {
    userid: null,
    i18n: {},
    context_url:null,
    endpoint: null,
    available_roles: [],
    entries: [],
    inherit: null,
    authtoken: null,
    requester: null,
    principal_search: null,
    isEditable: false,
  },

  beforeMount: function () {
    if (!this.$el.attributes['data-contexturl']){
      return;
    }

    this.context_url = this.$el.attributes['data-contexturl'].value;
    this.portal_url = this.$el.attributes['data-portalurl'].value;
    this.endpoint = this.context_url + '/@sharing';
    this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);
    this.authtoken = this.$el.attributes['data-authtoken'].value;
    this.isEditable = JSON.parse(this.$el.attributes['data-is-editable'].value);

    var requester = axios.create();
    requester.defaults.headers.common['Accept'] = 'application/json';
    requester.defaults.headers.common['Content-Type'] = 'application/json';
    this.requester = requester;
  },

  mounted: function () {
    this.fetchData();
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

    toggle_assignments: function (event, entry) {
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

    search: function() {
      // make sure IE 11 does not cache the fetch request
      var params = { _t: Date.now().toString(), search: this.principal_search };
      if (this.isEditable === false){
        params['ignore_permissions'] = 1
      }

      this.requester.get(this.endpoint, { params: params }).then(function (response) {

        this.entries = Object.values(this.entries).filter(i => i.disabled == false);
        this.entries = this.entries.concat(
          response.data['entries'].filter(i => i.disabled != false));
        this.inherit = response.data['inherit'];

      }.bind(this));
    },

    save: function(event){
      payload = {
        entries: Object.values(this.entries),
        inherit: this.inherit };

      this.requester.post(this.endpoint, payload).then(function (response) {
        // redirect to context and show statusmessage
        window.location = this.context_url + '/sharing/saved';
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
