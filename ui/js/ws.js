// window.onbeforeunload = function() {
//     websocketHandler.websocket.onclose = function () {}; // disable onclose handler first
//     websocketHandler.websocket.close();
// };
commonData = {
    version: '1.0.0',
    modules: [],
    tabs: [],
    target: "",
    selectedModule: {}
}

var WebsocketHandler= function() {
    this.connectionString = 'ws://'+window.location.hostname+':49999/';
    this.websocket = new WebSocket(this.connectionString);
    this.websocket.onopen = this.onOpen;
    this.websocket.onclose = this.onClose;
    this.websocket.onmessage = this.onMessage;
    this.websocket.onerror = this.onError;
};

WebsocketHandler.prototype = {
    initData: function (evt) {
        var hello = function() {
            var promise = new RSVP.Promise(function(resolve, reject) {
                guiCommandsHandler.hello(function(res) {
                    resolve(res);
                })                
            })
            return promise;
        };
        var getAllData = function() {
            var promise = new RSVP.Promise(function(resolve, reject) {
                guiCommandsHandler.getAllData(function(res) {
                    resolve(res.args);
                })
            });
            return promise;
        };
        // Gets modules names, version, etc
        var getModulesLog = function() {
            var promise = new RSVP.Promise(function(resolve, reject) {
                guiCommandsHandler.getModulesLog(function(res) {
                    resolve(res.args);
                })
            });
            return promise;
        }
        return hello()
            .then(function(res) {
                return getAllData();
            })
            .then(function(args) {
                _.extend(commonData, args);
                return getModulesLog();
            })
            .then(function(args) {
                var tabsData = _.map(args, function(value, key) {
                    return {
                        title: key, 
                        content: _.map(value.message, function(message) {
                            if (message.type == 'image')
                                message.message =  'data:image/jpg;base64,' + message.message;
                            return message;
                        }),
                        active: true, 
                        useListener: _.size(value.listener) > 0,
                        listenerMessages: value.listener ? value.listener.message : "",
                        listenerState: value.listener ? value.listener.connected : 0,
                        state: value.state
                    }
                });
                _.extend(commonData, {tabs: tabsData});
                // console.log(args);
            })
    },
    onOpen: function(evt) {
        toastr.info('Connection to server succeeded');
        websocketHandler.initData(evt);
    },

    onClose: function(evt) {
        console.log("Close")
    },

    onMessage: function(evt) {
        // console.log(evt.data);
        serverCommandsHandler.parseAndExecuteMessage(evt.data);
    },

    onError: function(evt) {
        websocketHandler.websocket.close();
    },

    doSend: function(message) {
        websocketHandler.websocket.send(JSON.stringify(message));
    },

    reconnect: function(){
        websocketHandler.websocket.close();
        websocketHandler.websocket = new WebSocket(this.connectionString);
        websocketHandler.websocket.onopen = this.onOpen;
        websocketHandler.websocket.onclose = this.onClose;
        websocketHandler.websocket.onmessage = this.onMessage;
        websocketHandler.websocket.onerror = this.onError;
    }
}    



websocketHandler = new WebsocketHandler();
function doSend(message){
    websocketHandler.doSend(message);
}
function bindEvent(event_type, callback) {
      $(document).unbind(event_type);
      $(document).on(event_type, callback);
}

