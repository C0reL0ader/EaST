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
        // Gets modules names, version, etc
        guiCommandsHandler.getAllData(function(evt) {
            var oData = evt.args;
            this.oModulesInfoModel = new sap.ui.model.json.JSONModel();
            this.oModulesInfoModel.setData(oData);
            mainView.setModel(this.oModulesInfoModel);
        });
        mainController.setConnectionState(true);
        showMessageBox("Connected to "+this.websocket.url);
        if (!window.statusTimer) {
            //Check for log and listener messages every 300ms
            statusTimer = setInterval(mainController.getModulesLog, 300);
        }
    },

    onOpen: function(evt) {
        websocketHandler.initData(evt);
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
        showMessageBox('Disconnected from server');
        websocketHandler.websocket.close();
    },

    doSend: function(message) {
        websocketHandler.websocket.send(JSON.stringify(message));
    },

    reconnect: function(){
        websocketHandler.websocket = new WebSocket(this.connectionString);
        websocketHandler.websocket.onopen = bind(this.onOpen, this);
        websocketHandler.websocket.onclose = this.onClose;
        websocketHandler.websocket.onmessage = this.onMessage;
        websocketHandler.websocket.onerror = this.onError;
    }
}
