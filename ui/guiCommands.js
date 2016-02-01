var GuiCommandsHandler = function() {
};

GuiCommandsHandler.prototype = {
    hello: function() {
        doSend({"hello":{"name": "EastUI", "type":"ui"}})
    },
    
    showOptions: function(module_name, callback) {
        bindEvent("on_show_options", callback);
        doSend({ "command": "options", "args": { "module_name": module_name }});
    },
    
    getAllData: function(callback){
        bindEvent("on_get_all_data", callback);
        doSend({ "command": "get_all_server_data", "args": ""});
    },

    sendListenerCommand: function(module_name, message, callback){
        doSend({
            "command": "gui_command_to_listener",
            "args": {
                "module_name": module_name,
                "message": message
            }
        });
    },
   
    startModule: function(args, callback){
        bindEvent("on_module_started", callback);
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

    getSource: function(module_name, callback){
        bindEvent("on_get_source", callback);
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
    },

    getModulesLog: function(callback) {
        bindEvent("on_modules_log", callback)
        req = {
            "command": "on_modules_log",
            "args": ""
        }
        doSend(req);
    },

};