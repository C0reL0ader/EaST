function ServerCommandsHandler() {
    this.commands = {"info": this.showModuleInfo,
                     "options": this.showOptions,
                     "start_module": this.startModule,
                     "restore_tabs": this.restoreTabs,
                     "set_all_data": this.setAllData,
                     "on_listener_message": this.onListenerMessage,
                     "get_source": this.getSource,
                     "on_modules_log": this.onModulesLog,
                     "on_module_message": this.onModuleMessage,
                     "hello": this.onHello
                    };
    this.statuses = [];
};

ServerCommandsHandler.prototype = {

    startModule: function(args){
        serverCommandsHandler.fireCustomEvent("on_module_started", args);
    },

    setAllData: function(args){
        serverCommandsHandler.fireCustomEvent("on_get_all_data", args);
    },

    onModulesLog: function(args) {
        serverCommandsHandler.fireCustomEvent("on_modules_log", args);
    },

    onListenerMessage: function(args){
        serverCommandsHandler.fireCustomEvent("on_listener_message", args);
    },

    showOptions: function(args){
        serverCommandsHandler.fireCustomEvent("on_show_options", args);
    },

    getSource: function(args) {
        serverCommandsHandler.fireCustomEvent("on_get_source", args);
    },

    parseAndExecuteMessage: function(message){
        var parsed = JSON.parse(message);
        var command = parsed["command"];
        var args = parsed["args"];
        this.commands[command](args);
    },

    onModuleMessage: function (args) {
        serverCommandsHandler.fireCustomEvent("on_module_message", args);
    },

    onHello: function(args) {
        serverCommandsHandler.fireCustomEvent("hello", args);
    },

    fireCustomEvent: function(event_type, data) {
        $.event.trigger({
            type: event_type,
            args: data
        });
    }
};