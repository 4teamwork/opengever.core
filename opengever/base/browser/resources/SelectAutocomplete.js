(function(global, $) {
  "use strict";

  var SelectAutocomplete = function(options) {

    options = $.extend({
      target: "select"
    }, options);

    var Select = function(target) {

      var self = this;

      var extractSource = function() {
        return $.map($("option", target), function(option) {
          return {
            label: option.innerHTML,
            value: option.innerHTML,
            id: option.value
          };
        });
      };

      this.element = $("<input type='text' />").addClass("select-autocomplete");

      this.clear = function() { this.element.val(""); };

      this.select = function(value) {
        this.selected = value;
        this.sync();
      };

      this.label = function() { return $(":selected", target).text(); };

      this.abort = $.proxy(function() {
        this.element.val(this.label());
        this.element.removeClass("searching");
      }, this);

      this.start = $.proxy(function() {
        this.search("");
        this.clear();
        this.element.addClass("searching");
      }, this);

      this.sync = $.proxy(function() {
        target.val(this.selected);
        target.trigger("change");
        this.element.val($(":selected", target).text());
        this.element.blur();
      }, this);

      this.on = function(event, callback) { this.element.on(event, callback); };

      this.selected = target.val();

      this.element.data("target", target);
      $.extend(this, $.ui.autocomplete({
        source: extractSource(target),
        minLength: 0,
        delay: 0
      }, this.element));

      this.element.insertAfter(target);
      target.hide();

      this.on("autocompleteselect", function(event, ui) {
        self.select(ui.item.id);
      });

      this.on("focus", this.start);

      this.on("blur", this.abort);

      this.sync();

    };

    var renderMenu = function(ul, items) {
      var self = this;
      $.each(items, function(index, item) {
        self._renderItemData(ul, item);
      });
    };

    var renderItem = function(ul, item) {
      var li = $("<li>")
               .data("ui-autocomplete-item", item)
               .addClass("ui-menu-item")
               .append($("<a>").text(item.label));
      return ul.append(li);
    };

    var build = function(buildTarget) {
      var widget = new Select(buildTarget);
      widget._renderItem = renderItem;
      widget._renderMenu = renderMenu;
    };

    $(options.target).each(function() { build($(this)); });

  };

  global.SelectAutocomplete = SelectAutocomplete;

}(window, jQuery));
