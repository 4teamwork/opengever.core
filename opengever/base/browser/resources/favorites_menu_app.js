$(init);
function init() {
  var app = new Vue({
    template: '#favorites-menu-list',
    el: '#favorite-vue-app',
    data: {
      userid: null,
      i18n: {},
      overviewurl: null,
      entpoint: null,
      entries: [],
      requester: null,
      showFavorites: false,
      isOpen: false,
    },

    beforeMount: function () {
      if (!this.$el.attributes['data-userid']){
        return;
      }

      var portalurl = this.$el.attributes['data-portalurl'].value;
      this.overviewurl = this.$el.attributes['data-overviewurl'].value;
      this.userid = this.$el.attributes['data-userid'].value;
      this.endpoint = portalurl + '/@favorites/' + this.userid;
      this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);

      var requester = axios.create();
      requester.defaults.headers.common['Accept'] = 'application/json';
      requester.defaults.headers.common['Content-Type'] = 'application/json';
      this.requester = requester;
    },

    computed: {
      messenger: MessageFactory.getInstance
    },

    methods: {
      isSameElement: function(target) {
        return target !== this.$el && !this.$el.contains(target);
      },
      handleClickOutside: function(event) {
        if (this.isSameElement(event.target)) {
          this.close();
        }
      },
      toggle: function() {
        if (this.isOpen) {
          return this.close()
        } else {
          return this.open();
        }
      },
      open: function() {
        return this.fetchData()
          .then(function() {
            this.isOpen = true
          }.bind(this));
      },
      close: function() {
        this.isOpen = false;
      },
      fetchData: function () {
        // make sure IE 11 does not cache the fetch request
        var url = this.endpoint + '?_t=' + Date.now().toString();
        return this.requester.get(url)
          .then(function (response) {
          var items = response.data.sort(function(a, b){
            return a.position - b.position;
          });

          this.entries = [];
          this.$nextTick(function(){
            this.entries = items;
          }.bind(this));

        }.bind(this));
      },
    },
    created: function() {
      document.addEventListener('click', this.handleClickOutside)
    }
  });
}
