/**
 * Tree node
 *
 * https://retreaver.com/call_buyers/new
 * Call Buyer Properties
 *
 */

Vue.component('re-advertiser-properties', {
    template: [
        '<div>',
            '<re-panel',
                'title="Advertiser properties"',
                '>',
                '<div class="form-group">',
                    '<label>Number:</label>',
                    '<input class="form-control" v-model="number">',
                '</div>',
                '<div class="form-group">',
                    '<label>Name:</label>',
                    '<input class="form-control" v-model="name">',
                '</div>',
                '<div class="form-group">',
                    '<label>Advertiser ID:</label>',
                    '<input class="form-control" v-model="advertiser_id">',
                '</div>',
                '<div class="form-group">',
                    '<label>Timeout:</label>',
                    '<re-spinner',
                        ':model.sync="timeout"',
                        'min="0"',
                        '>',
                    '</re-spinner>',
                '</div>',
                '<div class="form-group">',
                    '<label>Timer offset:</label>',
                    '<re-spinner',
                        ':model.sync="timer_offset"',
                        'min="0"',
                        '>',
                    '</re-spinner>',
                '</div>',
                '<div class="form-group">',
                    '<label>Send digits:</label>',
                    '<input class="form-control" v-model="digits">',
                '</div>',
            '</re-panel>',
        '</div>',
    ].join(' '),
    props: {
        id: {
            // type: String,
            default: '',
        },
        number: {
            // type: String,
            default: '',
        },
        name: {
            // type: String,
            default: '',
        },
        advertiser_id: {
            // type: String,
            default: '',
        },
        timeout: {
            // type: Number,
            default: 30,
        },
        timer_offset: {
            // type: Number,
            default: 0,
        },
        digits: {
            // type: String,
            default: '',
        },
    },
    data: function() {
        return {
        };
    },
    computed: {
    },
    methods: {
    },
    ready: function() {
    },
});
