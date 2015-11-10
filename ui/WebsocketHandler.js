var WebsocketHandler= function() {
    this.connectionString = 'ws://'+window.location.hostname+':49999/';
    this.websocket = new WebSocket(this.connectionString);
    this.websocket.onopen = bind(this.onOpen, this);
    this.websocket.onclose = this.onClose;
    this.websocket.onmessage = this.onMessage;
    this.websocket.onerror = this.onError;
};

WebsocketHandler.prototype = {
    initData: function (evt) {
        jQuery.sap.require("sap.m.MessageBox");
        guiCommandsHandler.getAllData(doSend);
        mainController.setConnectionState(true);
        sap.m.MessageToast.show("Connected to "+this.websocket.url, {my:"center center", at:"center center", duration:1000});
        guiCommandsHandler.restoreTabs(doSend);
    },

    onOpen: function(evt) {
        bind(this.initData(evt), this);
        console.log("Websocket opened");
    },

    onClose: function(evt) {
        if (window.statusTimer){
            clearTimeout(window.statusTimer);
            window.statusTimer = null;
        }
        mainController.setConnectionState(false);
    },

    onMessage: function(evt) {
        serverCommandsHandler.parseAndExecuteMessage(evt.data);
        //console.log(evt.data);
    },

    onError: function(evt) {
        jQuery.sap.require("sap.m.MessageBox");
        sap.m.MessageBox.alert('Disconnected from server');
        this.websocket.close();
    },

    doSend: function(message) {
        this.websocket.send(JSON.stringify(message));
    },

    reconnect: function(){
        this.websocket = new WebSocket(this.connectionString);
        this.websocket.onopen = bind(this.onOpen, this);
        this.websocket.onclose = this.onClose;
        this.websocket.onmessage = this.onMessage;
        this.websocket.onerror = this.onError;
    }
}
