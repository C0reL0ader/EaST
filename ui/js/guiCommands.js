var GuiCommandsHandler = function() {
};

GuiCommandsHandler.prototype = {
    hello: function(callback) {
        var data = {hello:{name: 'EastUI', type:'ui'}};
        doSend(data, callback);
    },
    
    showOptions: function(module_name, callback) {
        var data = {command: 'get_module_options', args: { module_name: module_name }};
        doSend(data, callback);
    },
    
    getAllData: function(callback){
        var data = {command: 'get_all_server_data', args: ''};
        doSend(data, callback);
    },

    sendListenerCommand: function(module_name, message, callback){
        var data = { command: 'gui_command_to_listener', args: { module_name: module_name, message: message }};
        doSend(data, callback);
    },
   
    startModule: function(args, callback){
        var data = { command: 'start_module', args: args };
        doSend(data, callback);
    },

    killProcess: function(tabName){
        var data = {command: 'kill_process', args: {module_name: tabName}};
        doSend(data);
    },

    getSource: function(module_name, callback){
        var data = {command: 'get_source', args: {'module_name': module_name}};
        doSend(data, callback);
    },

    saveSource: function(module_name, code) {
        var data = {command: 'save_source', args: {'module_name': module_name, 'message': code}};
        doSend(data);
    },

    installViaPip: function(library_name, callback) {
        var data = { command: 'install_via_pip', args: {'library_name': library_name}}
        doSend(data, callback);
    },

    getModulesLog: function(callback) {
        var data = {command: 'get_modules_log', args: {}}
        doSend(data, callback);
    },

    createModule: function(module_name) {
        var data = {command: 'create_module', args: {'module_name': module_name}}
        doSend(data)
    },
};
guiCommandsHandler = new GuiCommandsHandler();

function genUUID4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}
function bindEvent(event_type, callback) {
    $(document).unbind(event_type);
    $(document).on(event_type, callback);
}