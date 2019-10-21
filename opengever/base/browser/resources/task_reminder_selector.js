$(function() {
  $(document).on('reload', function() {
    if (window.tabbedview) {
      if (document.querySelector('#task-reminder-selector')) {
        var initState = $('#task-reminder-selector').data('state');
        var viewName = window.tabbedview.prop('view_name');
        var taskReminderApp = new Vue({
          el: '#task-reminder-selector',
          template: '#task-reminder-selector-vue-template',
          data: {
            reminderOptions: initState.reminder_options,
            endpoint: initState.endpoint,
            isLoading: false,
            errorMsg: initState.error_msg,
            currentErrorMsg: '',
            nextSelectedOption: null,
            noReminderIdentifier: 'no-reminder',
            onDateReminderIdentifier: 'on_date',
          },
          computed: {
            currentTitle: function() {
              if (this.currentErrorMsg !== '') { return this.currentErrorMsg; }
              if (this.currentReminder.option_type === this.onDateReminderIdentifier) {
                return new Date(this.currentReminder.params.date).format('d.m.Y');
              } else {
                return this.currentReminder.option_title;
              }
            },
            orderedOptions: function() {
              return this.reminderOptions.sort(function(a, b) {
                return a.sort_order - b.sort_order;
              });
            },
            currentReminder: function() {
              return this.reminderOptions.filter(function(option) {
                return option.selected === true;
              })[0];
            },
          },
          methods: {
            handleSetReminder: function(option, params) {
              if (this.isLoading) { return; }

              this.resetErrorMsg();

              var previousOption;
              previousOption = this.currentReminder;
              if (previousOption.option_type === option.option_type && option.option_type !== this.onDateReminderIdentifier) { return; }

              this.isLoading = true;
              this.nextSelectedOption = option;
              this.nextSelectedOption.showSpinner = true;

              var request;

              var payload = {option_type: option.option_type, params: {}};
              if (typeof(params) !== 'undefined') {
                Object.assign(payload, {params: params});
              }

              if (option.option_type === this.noReminderIdentifier) {
                request = this.requester.delete(this.endpoint);
              } else if (previousOption.option_type === this.noReminderIdentifier) {
                request = this.requester.post(this.endpoint, payload);
              } else {
                request = this.requester.patch(this.endpoint, payload);
              }

              request.then(function() {
                this.setReminder(option, params);
                this.finish_request();
              }.bind(this));

              request.catch(function() {
                this.setReminder(previousOption);
                this.handleError();
                this.finish_request();
              }.bind(this));

            },
            finish_request: function(){
              this.isLoading = false;
              this.longRequest = false;
              this.nextSelectedOption.showSpinner = false;
              this.nextSelectedOption = null;
            },
            setReminder: function(option, params) {
              this.reminderOptions.map(function(o) {
                o.selected = o === option;
                o.params = params;
              });
            },
            handleError: function(previousOption) {
              this.currentErrorMsg = this.errorMsg;
            },
            resetErrorMsg: function() {
              this.currentErrorMsg = '';
            },
          },
          beforeMount: function () {
            var requester = axios.create();
            requester.defaults.headers.common.Accept = 'application/json';
            requester.defaults.headers.common['Content-Type'] = 'application/json';
            this.requester = requester;
          },
        });
        Vue.component('reminder-option', {
          props: ['option'],
          template: '#task-reminder-selector-option-vue-template',
          methods: {
            clicked: function() {
              this.$emit('clicked', this.option);
            },
          },
        });
        Vue.component('reminder-option-on-date', {
          props: ['option'],
          template: '#task-reminder-selector-option-on-date-vue-template',
          computed: {
            datepickerConfig: function() {
              var tomorrow = new Date();
              tomorrow.setDate(tomorrow.getDate() + 1);

              var currentValue = '';
              if (this.option.params) {
                currentValue = this.toDatePickerValue(this.option.params.date)
              }

              return {
                onChangeDateTime: this.onChangeDateTime.bind(this),
                dayOfWeekStart: 1,
                format: 'd.m.Y',
                scrollInput: false,
                scrollMonth: false,
                scrollTime: false,
                timepicker: false,
                minDate: tomorrow,
                value: currentValue,
              };
            },
          },
          mounted: function() {
            $(this.$el).datetimepicker(this.datepickerConfig);
          },
          methods: {
            reinitDateTimePicker: function(newDate) {
              $(this.$el).datetimepicker('destroy');
              $(this.$el).datetimepicker(
                Object.assign({},
                  this.datepickerConfig,
                  {value: newDate}));
            },
            toDatePickerValue: function(value) {
              return new Date(value).format('d.m.Y');
            },
            clicked: function() {
              $(this.$el).datetimepicker('show');
            },
            onChangeDateTime: function(date) {
              this.$emit('clicked', this.option, {date: date.format('Y-m-d')});
              this.reinitDateTimePicker(date);
            }
          },
        });
        if (viewName && viewName === 'sharing') {
          new Vue(taskReminderApp);
        }
      }
    }
  });
});
