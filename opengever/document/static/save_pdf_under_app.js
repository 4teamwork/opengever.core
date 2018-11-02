$(init);
function init() {
  var FIRST_POLL_INTERVAL = 500;
  var POLL_INTERVAL = 2000;
  var POLL_TIMEOUT = 60000;

  var app = new Vue({
    template: '#save-document-pdf',
    el: '#save-document-pdf-vue-app',
    data: {
      i18n: {},
      isFinished: false,
      isFailed: false,
      isTimeout: false,
      isError: false,
      sourcedocumenturl: null,
      destinationdocumenturl: null,
      statusurl: null,
    },

    beforeMount: function () {
      var portalurl = this.$el.attributes['data-portalurl'].value;
      this.statusurl = this.$el.attributes['data-statusurl'].value;
      this.sourcedocumenturl = this.$el.attributes['data-sourcedocumenturl'].value;
      this.destinationdocumenturl = this.$el.attributes['data-destinationdocumenturl'].value;
      this.i18n = JSON.parse(this.$el.attributes['data-i18n'].value);

      var requester = axios.create();
      requester.defaults.headers.common['Accept'] = 'application/json';
      requester.defaults.headers.common['Content-Type'] = 'application/json';
      this.requester = requester;

      this.pollingInitiated = Date.now();
      this.fetchData();
    },

    mounted: function () {
      setTimeout(function () {
        this.fetchData();
      }.bind(this), FIRST_POLL_INTERVAL);
    },

    methods: {
      fetchData: function () {
        // Make sure IE 11 does not cache the fetch request
        var url = this.statusurl + '?_t=' + Date.now().toString();

        // abort if timeout exceeded
        if (Date.now() - this.pollingInitiated > POLL_TIMEOUT) {
          this.isTimeout = true;
          this.isError = true;
          return;
        }

        // poll for status
        return this.requester.get(url)
          .then(function (response) {
            if (response.data['conversion-status']=='conversion-successful') {
              this.isFinished = true;
            } else if (response.data['conversion-status']=='conversion-failed') {
              this.isFailed = true;
            } else if (response.data['conversion-status']=='conversion-skipped') {
              this.isFailed = true;
            }
             else {
              setTimeout(function () {
                this.fetchData();
              }.bind(this), POLL_INTERVAL);
            }
        }.bind(this))
        .catch(function (error) {
          this.isError = true;
        }.bind(this));
      }
    }
  });
}
