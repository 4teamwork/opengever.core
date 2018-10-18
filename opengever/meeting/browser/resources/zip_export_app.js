$(init);
function init() {
  var FIRST_POLL_INTERVAL = 500;
  var POLL_INTERVAL = 2000;
  var POLL_TIMEOUT = 60000;

  var app = new Vue({
    template: '#meeting-zip-export',
    el: '#meeting-zip-export-vue-app',
    data: {
      i18n: {},
      isFinished: false,
      isTimeout: false,
      isError: false,
      isDocumentSkipped: false,
      downloadurl: null,
      pollurl: null,
      meetingurl: null,
    },

    beforeMount: function () {
      var portalurl = this.$el.attributes['data-portalurl'].value;
      this.pollurl = this.$el.attributes['data-pollurl'].value;
      this.downloadurl = this.$el.attributes['data-downloadurl'].value;
      this.meetingurl = this.$el.attributes['data-meetingurl'].value;
      this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);

      var requester = axios.create();
      requester.defaults.headers.common['Accept'] = 'application/json';
      requester.defaults.headers.common['Content-Type'] = 'application/json';
      this.requester = requester;

      this.pollingInitiated = Date.now();
    },

    mounted: function () {
      setTimeout(function () {
        this.fetchData();
      }.bind(this), FIRST_POLL_INTERVAL);
    },

    methods: {
      fetchData: function () {
        // Make sure IE 11 does not cache the fetch request
        var url = this.pollurl + '&_t=' + Date.now().toString();

        // abort if timeout exceeded
        if (Date.now() - this.pollingInitiated > POLL_TIMEOUT) {
          this.isTimeout = true;
          this.isError = true;
          return;
        }

        // poll for status
        return this.requester.get(url)
          .then(function (response) {
            if (response.data['is_finished']) {
              this.isFinished = true;
              if (response.data['skipped'] > 0) {
                this.isDocumentSkipped = true;
              }
            } else {
              setTimeout(function () {
                this.fetchData();
              }.bind(this), POLL_INTERVAL)
            }
        }.bind(this))
        .catch(function (error) {
          this.isError = true;
        }.bind(this));
      }
    }
  });
}
