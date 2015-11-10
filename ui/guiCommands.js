function bind(func, context) {
  return function() {
    return func.apply(context, arguments);
  };
}

var GuiCommandsHandler = function() {
};

GuiCommandsHandler.prototype = {
    startListener: function(send) {
        send({"command": "run_listener", "args": ""})
    },
    
    showOptions: function(module_name, send) {
        send({ "command": "options", "args": { "module_name": module_name }});
    },
    
    getAllData: function(send){
        send({ "command": "get_all_server_data", "args": ""});
    },

    restoreTabs: function(send){
        send({ "command": "restore_tabs", "args": ""});
    },

    sendListenerCommand: function(module_name, message, send){
        send({
            "command": "gui_command_to_listener",
            "args": {
                "module_name": module_name,
                "message": message
            }
        });
    },
   
    startModule: function(args){
        doSend({
            "command": "exploit",
            "args": args,
        });
    },

    killProcess: function(tabName){
        req = {};
        req["command"] = "kill_process";
        req["args"] = {"module_name": tabName};
        doSend(req);
    },

    getSource: function(module_name){
        req={};
        req["command"] = "get_source";
        req["args"] = {"module_name": module_name};
        doSend(req);
    },

    saveSource: function(module_name, code) {
        req={};
        req["command"] = "save_source";
        req["args"] = {"module_name": module_name, "message": code};
        doSend(req);
    }

};