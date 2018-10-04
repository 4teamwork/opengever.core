$(function() {
    var initState = $('#task-reminder-selector').data('state');
    Vue.component('reminder-option', {
        props: ['selected', 'title', 'showSpinner'],
        template: `
        <li>
            <a href="#" @click.prevent="clicked">
                <span class="taskReminderSelectorOptionIcon">
                    <span class="fa" :class="{
                        'fa-check': selected,
                        'fa-spinner fa-spin': showSpinner }">
                    </span>
                </span>
                <span class="subMenuTitle actionText">{{title}}</span>
            </a>
        </li>
        `,
        methods: {
            clicked: function() {
                this.$emit('clicked');
            },
        },
    });

    var app = new Vue({
        el: '#task-reminder-selector',
        template: `
        <dl class="dropdown_button">
            <dt class="">
              <span class="taskReminderSelectorCurrent">{{currentTitle}}</span>
            </dt>
            <dd>
                <ul class="taskReminderSelectorOptions">
                    <reminder-option v-for="option in orderedOptions"
                                     @clicked="handleSetReminder(option)"
                                     :selected="option.selected"
                                     :showSpinner="showSpinnerForOption(option)"
                                     :title="option.option_title" />
                </ul>
            </dd>
        </dl>
        `,
        data: {
            reminderOptions: initState.reminder_options,
            endpoint: initState.endpoint,
            isLoading: false,
            errorMsg: initState.error_msg,
            currentErrorMsg: "",
            longRequest: false,
            nextSelectedOption: null,
            spinnerTimeout: 100,
            noReminderIdentifier: 'no-reminder',
        },
        computed: {
            currentTitle: function() {
                if (this.currentErrorMsg !== '') { return this.currentErrorMsg };
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

                previousOption = this.currentReminder();
                if (previousOption === option) { return; }

                this.isLoading = true;
                this.nextSelectedOption = option

                var request;
                if (option.option_type === this.noReminderIdentifier) {
                    request = this.requester.delete(this.endpoint);
                } else if (previousOption.option_type === this.noReminderIdentifier) {
                    request = this.requester.post(this.endpoint, option);
                } else {
                    request = this.requester.patch(this.endpoint, option);
                }

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
                this.currentErrorMsg = "";
            },
            showSpinnerForOption: function(option) {
                return this.longRequest && option === this.nextSelectedOption
            },
            handleLongRequest: function() {
                this.longRequest = true;
            }
        },
        beforeMount: function () {
            var requester = axios.create();
            requester.defaults.headers.common['Accept'] = 'application/json';
            requester.defaults.headers.common['Content-Type'] = 'application/json';
            this.requester = requester;
        },
    });
});
