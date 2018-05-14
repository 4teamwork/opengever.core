var app = new Vue({
  template: '#favorites-list',
  el: '#favorite-view-vue-app',
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

  created: function() {
    window.addEventListener('favorites-tree:changed',this.fetchData);
  },
  destroyed: function() {
    window.removeEventListener('favorites-tree:changed', this.fetchData);
  },

  directives: {
    focus: { inserted: function (el) { el.focus(); }}
  },

  computed: {
    messenger: MessageFactory.getInstance,
  },

  methods: {

    errorMessage: function (){
      return this.messenger.shout([{
        'messageTitle': this.i18n.message_title,
        'message': this.i18n.message_not_saved, 'messageClass': 'error'}]);
    },

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
      // make sure IE 11 does not cache the fetch request
      var url = this.endpoint+ '?_t=' + Date.now().toString();
      this.requester.get(url).then(function (response) {
        var items = response.data.sort(function(a, b){
          if (a.position > b.position) {
            return 1;
          } else if (a.position < b.position) {
            return -1;
          }
          return 0;
        });

        self.entries = [];
        self.$nextTick(function(){
          self.entries = items;
        });

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
      this.requester.patch(this.editEntry['@id'], payload).then(function (response) {
        if (response.status === 204) {
          self.editEntry.title = payload.title;
          self.newTitle = '';
          self.closeOverlay();
        } else {
          self.errorMessage();
        }
      }).catch(function(){
        self.errorMessage();
      });
    },

    deleteAction: function (entry) {
      var self = this;
      var payload = {
        _authenticator: this.authtoken,
        title: this.newTitle
      };
      this.requester.delete(entry['@id'], payload).then(function (response) {
        if (response.status === 204) {
          self.fetchData();
          $(window).trigger('favorites:changed');
        } else {
          self.errorMessage();
        }
      }).catch(function(){
        self.errorMessage();
      });
    },

    updatePosition: function (entry, newPosition, oldPosition) {
      var self = this;
      var payload = {
        _authenticator: this.authtoken,
        position: newPosition};
      this.requester.patch(entry['@id'], payload).then(function (response) {
        if (response.status === 204) {
          self.fetchData();
        } else {
          self.errorMessage();
        }
      }).catch(function(){
        self.errorMessage();
      });
    },

    makeSortable: function(){
      var self = this;
      $('.favorites tbody').sortable({
        handle: '.moveHandler',
        placeholder: '.favorites-placeholder',
        helper: 'clone',
        forcePlaceholderSize: true,
        start: function(e, ui) {
          ui.item.data('oldPosition', ui.item.index());
        },
        update: function(e, ui) {
          var oldPosition = ui.item.data('oldPosition');
          var entry = self.entries[oldPosition];
          self.updatePosition(entry, ui.item.index(), oldPosition);
        }
      });
    },
  },
});
