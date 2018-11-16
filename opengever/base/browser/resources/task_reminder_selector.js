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
            longRequest: false,
            nextSelectedOption: null,
            spinnerTimeout: 100,
            noReminderIdentifier: 'no-reminder',
          },
          computed: {
            currentTitle: function() {
              if (this.currentErrorMsg !== '') { return this.currentErrorMsg; }
              return this.currentReminder().option_title;
            },
            orderedOptions: function() {
              return this.reminderOptions.sort(function(a, b) {
                return a.sort_order - b.sort_order;
              });
            }
          },
          methods: {
            currentReminder: function() {
              return this.reminderOptions.filter(function(option) {
                return option.selected === true;
              })[0];
            },
            handleSetReminder: function(option) {
              if (this.isLoading) { return; }

              this.resetErrorMsg();

              var previousOption;
              previousOption = this.currentReminder();
              if (previousOption === option) { return; }

              this.isLoading = true;
              this.nextSelectedOption = option;

              var request;
              if (option.option_type === this.noReminderIdentifier) {
                request = this.requester.delete(this.endpoint);
              } else if (previousOption.option_type === this.noReminderIdentifier) {
                request = this.requester.post(this.endpoint, option);
              } else {
                request = this.requester.patch(this.endpoint, option);
              }

              var timer;
              timer = window.setTimeout(
                this.handleLongRequest, this.spinnerTimeout);

              request.then(function() {
                this.setReminder(option);
              }.bind(this));

              request.catch(function() {
                this.setReminder(previousOption);
                this.handleError();
              }.bind(this));

              request.finally(function() {
                window.clearTimeout(timer);
                this.isLoading = false;
                this.longRequest = false;
                this.nextSelectedOption = null;
              }.bind(this));
            },
            setReminder: function(option) {
              this.reminderOptions.map(function(o) {
                o.selected = o === option;
              });
            },
            handleError: function(previousOption) {
              this.currentErrorMsg = this.errorMsg;
            },
            resetErrorMsg: function() {
              this.currentErrorMsg = '';
            },
            showSpinnerForOption: function(option) {
              return this.longRequest && option === this.nextSelectedOption;
            },
            handleLongRequest: function() {
              this.longRequest = true;
            }
          },
          beforeMount: function () {
            var requester = axios.create();
            requester.defaults.headers.common.Accept = 'application/json';
            requester.defaults.headers.common['Content-Type'] = 'application/json';
            this.requester = requester;
          },
        });
        Vue.component('reminder-option', {
          props: ['selected', 'title', 'showSpinner'],
          template: '#task-reminder-selector-option-vue-template',
          methods: {
            clicked: function() {
              this.$emit('clicked');
            },
          },
        });
        if (viewName && viewName === 'sharing') {
          new Vue(taskReminderApp);
        }
      }
    }
  });
});
