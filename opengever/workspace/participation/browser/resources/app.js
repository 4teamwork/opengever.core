var app = new Vue({
  template: '#participants-table',
  el: '#vue-app',
  data: {
    i18n: {},
    entpoint: null,
    entries: [],
    authtoken: null,
    isDeleting: false,
    isModifying: false,
  },

  beforeMount: function () {
    this.endpoint = this.$el.attributes['data-endpoint'].value;
    this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);
    this.authtoken = this.$el.attributes['data-authtoken'].value;
  },

  mounted: function () {
    this.fetchData();
    this.initSelect2();
  },

  computed: {
    ajaxOptions: function () {
      return JSON.stringify(
        { url: this.endpoint + '/search', 'dataType': 'json', 'delay': 250 });
    },
    select2Config: function () {
      return JSON.stringify(
        { minimumInputLength: 3, width: '300px', i18n: this.i18n });
    },

    roles: function() {
      return [
        {name: this.i18n.workspaceguest, value: 'WorkspaceGuest'},
        {name: this.i18n.workspacemember, value: 'WorkspaceMember'},
        {name: this.i18n.workspaceadmin, value: 'WorkspaceAdmin'},
      ];
    },

    messanger: MessageFactory.getInstance,
  },

  methods: {
    fetchData: function () {
      var self = this;
      axios.get(this.endpoint).then(function (response) {
        self.entries = response.data;
      });
    },

    initSelect2: function () {
      window.ftwKeywordWidget.initWidget(jQuery('select[name="userid"]'));
      jQuery('select[name="role"]').select2({ width: '150px'} );
    },

    updateRoleForUser: function (entry, event) {
      var self = this;
      var payload = new FormData();
      var newRole = event.currentTarget.value;

      self.isModifying = true;
      payload.append('token', entry.token);
      payload.append('role', event.currentTarget.value);
      payload.append('type', entry.type_);
      payload.append('_authenticator', this.authtoken);
      axios.post(this.endpoint + '/modify', payload).then(function (response) {
        if (response.status === 204) {
          entry.roles = [newRole];
          self.isModifying = false;
          self.messanger.shout([{'messageTitle': 'Info', 'message': 'Rolle wurde aktualisiert', 'messageClass': 'info'}]);
        }
      });
    },

    inviteUser: function () {
      var payload = new FormData();
      payload.append('userid', this.$refs.userid.value);
      payload.append('role', this.$refs.role.value);
      payload.append('_authenticator', this.authtoken);

      var self = this;
      axios.post(this.endpoint + '/add', payload).then(function (response) {
        self.entries = response.data;
        jQuery('select[name="userid"]').val('').trigger('change');
        jQuery('select[name="role"]').val('WorkspaceGuest').trigger('change');
        self.messanger.shout([{'messageTitle': 'Info', 'message': 'Teilnehmer wurde eingeladen', 'messageClass': 'info'}]);
      });
    },

    deleteUser: function (entry) {
      this.isDeleting = true;
      var payload = new FormData();
      payload.append('token', entry.token);
      payload.append('type', entry.type_);
      payload.append('_authenticator', this.authtoken);

      var self = this;
      axios.post(this.endpoint + '/delete', payload).then(function (response) {
        self.entries = response.data;
        self.isDeleting = false;
        self.messanger.shout([{'messageTitle': 'Info', 'message': 'Teilnehmer wurde gelöscht', 'messageClass': 'info'}]);
      });
    },
  },
});
