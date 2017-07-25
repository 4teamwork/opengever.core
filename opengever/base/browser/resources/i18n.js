(function(global, $) {

  var translationEndpoint = global.portal_url + '/@i18n';

  var translations = {
    data: {},
    _update: function(data) { this.data = data; },
    _exists: function(key) { return this.data.hasOwnProperty(key); },
    _getFromCache: function(key) {
      var translation = $.Deferred();
      if (this._exists(key)) {
        translation.resolve(this.data[key]);
      } else {
        translation.reject(new Error('key: ' + key + ' could not be found'));
      }
      return translation;
    },
    _load: function() {
      return $.ajax(translationEndpoint, { headers: { 'Accept': 'application/json' } })
        .done(function(data) { this._update(JSON.parse(data)); }.bind(this)); },
    get: function(key) {
      var translation = $.Deferred();
      this._getFromCache(key)
        .done(translation.resolve)
        .fail(function() {
          this._load()
            .done(function() {
              this._getFromCache(key)
                .done(translation.resolve)
                .fail(translation.reject);
            }.bind(this))
            .fail(translation.reject);
        }.bind(this));

      return translation;
    },
  };

  function i18n(key) { return translations.get(key); }

  global.i18n = i18n;

})(window, window.jQuery);
