
Vue.config.devtools = true;

var app = new Vue({
  template: '#favorites-list',
  el: '#vue-app',
  data: {
    userid: null,
    i18n: {},
    entpoint: null,
    entries: [],
    authtoken: null,
    requester: null,
    showOverlay: false,
    editEntry: null,
    newTitle: '',
  },

  beforeMount: function () {
    var portalurl = this.$el.attributes['data-portalurl'].value;
    this.userid = this.$el.attributes['data-userid'].value;
    this.endpoint = portalurl + '/@favorites/' + this.userid;
    this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);
    this.authtoken = this.$el.attributes['data-authtoken'].value;

    var requester = axios.create();
    requester.defaults.headers.common['Accept'] = 'application/json';
    requester.defaults.headers.common['Content-Type'] = 'application/json';
    this.requester = requester;
  },

  mounted: function () {
    this.fetchData();
  },

  directives: {
    focus: { inserted: function (el) { el.focus(); }}
  },

  computed: {
  },

  methods: {

    handleUpdate: function(event) {
      this.newTitle = event.target.value;
    },

    handleEnterAndEsc: function(event) {
      switch (event.key) {
        case 'Enter':
          this.saveAction();
          break;
        case 'Escape':
          this.cancelAction();
          break;
      }
    },

    fetchData: function () {
      var self = this;
      this.requester.get(this.endpoint).then(function (response) {
        self.entries = response.data;
        self.reorder();
        self.makeSortable();
      });
    },

    openOverlay: function(entry, event) {
      this.showOverlay = true;
      this.editEntry = entry;
      this.newTitle = entry.title;
    },

    closeOverlay: function(entry, event) {
      this.showOverlay = false;
    },

    cancelAction: function () {
      this.showOverlay = false;
    },

    saveAction: function (event) {
      var self = this;
      var payload = {
        _authenticator: this.authtoken,
        title: this.newTitle};
      this.requester.patch(this.endpoint + '/' + this.editEntry['@id'], payload).then(function (response) {
        if (response.status === 200) {
          self.editEntry.title = payload.title;
          self.newTitle = '';
          self.closeOverlay();
        }
      });
    },

    reorder: function(){
      this.entries.sort(function(a, b){
        if (a.position > b.position) {
          return 1;
        } else if (a.position < b.position) {
          return -1;
        }
        return 0;
      });
    },

    updatePosition: function (entry, position) {
      var self = this;
      var payload = {
        _authenticator: this.authtoken,
        position: position};
      this.requester.patch(this.endpoint + '/' + entry['@id'], payload).then(function (response) {
        if (response.status === 200) {
          entry.position = position;
        }
      });
    },

    makeSortable: function(){
      var self = this;
      $('.favorites').sortable({
        handle: '.moveHandler',
        placeholder: '.favorites-placeholder',
        start: function(e, ui) {
          ui.item.data('start', ui.item.index());
        },
        update: function(e, ui) {
          var oldPosition = ui.item.data('start');
          var entry = self.entries[oldPosition];
          self.updatePosition(entry, ui.item.index());
        }
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
        self.messenger.shout([{'messageTitle': 'Info', 'message': self.i18n.message_deleted, 'messageClass': 'info'}]);
      });
    },
  },
});
