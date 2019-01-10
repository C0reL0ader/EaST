function ServerCommandsHandler() {
  this.commands = {
    "on_listener_message": this.onListenerMessage,
    "on_module_message": this.onModuleMessage,
    "on_error": this.onError,
    "on_info": this.onInfo,
    "hello": this.onHello,
    "on_callback": this.onCallback
  };
  this.statuses = [];
};

ServerCommandsHandler.prototype = {

  parseAndExecuteMessage: function (message) {
    var parsed = JSON.parse(message);
    var command = parsed["command"];
    var args = parsed["args"];
    var uuid = parsed.uuid;
    if (!command)
      return
    this.commands[command](args, uuid);
  },

  onCallback: function (args, uuid) {
    serverCommandsHandler.fireCustomEvent(uuid, args);
    $(document).unbind(uuid);
  },

  onListenerMessage: function (args) {
    serverCommandsHandler.fireCustomEvent("on_listener_message", args);
  },

  onModuleMessage: function (args) {
    serverCommandsHandler.fireCustomEvent("on_module_message", args);
  },

  onHello: function (args) {
    serverCommandsHandler.fireCustomEvent("hello", args);
  },

  onError: function (args) {
    toastr.error(args.message, 'Error', {timeOut: 5000});
  },

  onInfo: function (args) {
    toastr.info(args.message);
  },

  fireCustomEvent: function (event_type, data) {
    $.event.trigger({
      type: event_type,
      args: data
    });
  }
};

serverCommandsHandler = new ServerCommandsHandler();