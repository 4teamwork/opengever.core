(function(global, $, Controller) {

  function FavoriteController() {
    Controller.call(this);

    this.toggle_favorite = function(target) {
      if ($('#mark-as-favorite').hasClass('loading')){
        return;
      }

      if ($('#mark-as-favorite').hasClass('is-favorite')){
        this.delete_favorite(target);
      } else {
        this.add_favorite(target);
      }
    };

    this.add_favorite = function(target) {
      url = $('#favorite-action').data('url');
      target.addClass('loading');

      return $.ajax({
        url: url,
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        data: JSON.stringify({
          oguid: $('#favorite-action').data('oguid')})
      }).done(function(data) {
        target.data('favorite-id', data['favorite_id']);
        target.addClass('is-favorite');
        target.removeClass('loading');
        $(window).trigger('favorites:changed');
      }).fail(function(data){

        if (data.status == 409){
          // favorite already exists
          target.data('favorite-id', data.responseJSON['favorite_id']);
          target.addClass('is-favorite');
        }

        target.removeClass('loading');
      });

    };

    this.delete_favorite = function(target) {
      var url = $('#favorite-action').data('url') + '/' + target.data('favorite-id');
      target.addClass('loading');

      $.ajax(url, {
        url: url,
        method: "DELETE",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }}).success(function() {
          target.data('favorite-id', null);
          target.removeClass('is-favorite');
          target.removeClass('loading');
          $(window).trigger('favorites:changed');
        }).fail(function(data) {
          if (data.status == 404){
            // favorite already removed
            target.removeClass('is-favorite');
            target.data('favorite-id', null);
          }
          target.removeClass('loading');
        });
    };

    this.events = [
      {
        method: "click",
        target: "#mark-as-favorite",
        callback: this.toggle_favorite
      }
    ];

    this.init();

  }

  new FavoriteController();

}(window, window.jQuery, window.Controller));
