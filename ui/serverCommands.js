function ServerCommandsHandler() {
    this.commands = {"show": bind(this.showAvailableModules),
                     "info": bind(this.showModuleInfo),
                     "options": bind(this.showOptions),
                     "message": bind(this.onMessageFromServer),
                     "use": bind(this.useModule),
                     "start_log": bind(this.startLog),
                     "status": bind(this.showStatus),
                     "kill": bind(this.killProcess),
                     "register_available_modules": bind(this.registerAvailableModules),
                     "restore_tabs": bind(this.restoreTabs),
                     "set_all_data": bind(this.setAllData),
                     "listener_message": bind(this.onListenerMessage),
                     "get_source": bind(this.getSource),
                    };
    this.statuses = [];
    this.waitingSymbol = "\\";
};
var waitingSymbols = ["\\", "|", "/", "-"];

ServerCommandsHandler.prototype = {

    startLog: function(args){
        /*
        * args keys: module_name, message, state        *
        * */
        if(args && args['module_name'])
            mainController.addTab(args['module_name'], args['listener']);
        statusTimer = setInterval(function() {
            this.doSend({
                "command": "status",
                "args": ""
            });
        }, 300);
    },

    genNextWaitSymbol: function() {
        var index = waitingSymbols.indexOf(this.waitingSymbol)
        if(index+1 < waitingSymbols.length) {
            this.waitingSymbol = waitingSymbols[index + 1];
        } else {
            this.waitingSymbol = waitingSymbols[0];
        }
    },

    showStatus: function(args){
        ///modulesTab[key][i]
        // key = module_name
        // i == 0 - tabLabel
        // i == 1 - tabHeader
        // i == 2 - tabListener
        // i == 3 - shell connected
        serverCommandsHandler.genNextWaitSymbol();

        Object.keys(args).forEach(function(key) {
            if(!modulesTabs.hasOwnProperty(key))
                return;
            var logMessage = args[key].message;
            var state = args[key].state;
            var isThereNewLogMessages = args[key].new_messages;
            var currentTab = modulesTabs[key][0].tab;
            var activeTabKey = mainController.getActiveTabKey();
            var logTabLabel = modulesTabs[key][0].text;
            var logPanel = modulesTabs[key][0].panel;

            //change title and content only for current active tab
            if (currentTab.getId() === activeTabKey) {
                if (state == null) {
                    logMessage += "\r\n" + serverCommandsHandler.waitingSymbol;
                    document.title = "In progress...";
                    logTabLabel.setText(logMessage);
                }
                else {
                    if(state) {
                        document.title = "Success";
                    } else {
                        document.title = "Failed";
                    }
                }
            }
            logTabLabel.setText(logMessage);
            if(isThereNewLogMessages){
                logTabLabel.setText(logMessage);
                var elem = logPanel.setScrollTop(logPanel.$().find('.sapUiPanelCont'))[0];
                if(elem)
                    elem.scrollHeight;
            }

            if(state!=null && modulesTabs[key][0].tab.getState() == null) {
                modulesTabs[key][0].tab.setState(state);
            }

            if(args[key].hasOwnProperty("listener")){
                var listener = args[key].listener;
                if(listener){
                    var message = listener.message;
                    var isShellConnected = listener.connected;
                    var isThereNewListenerMessages = listener.new_messages;
                    if (isThereNewListenerMessages){
                        var listenerPanel =  modulesTabs[key][1].panel;
                        modulesTabs[key][1].textView.setValue(message);
                        var elem = modulesTabs[key][1].textView.$();
                        elem.scrollTop(elem[0].scrollHeight);
                    }
                    if (isShellConnected) {
                        var listenerTitle = "Listener was connected to shell:";
                        if (!modulesTabs[key].hasOwnProperty("shellConnected")) {
                            serverCommandsHandler.showMessageBox("Shell connected to " + key + " listener");
                            modulesTabs[key]["shellConnected"]=true;
                        }
                        if (isShellConnected === 2){
                            var listenerTitle = "Listener was disconnected from shell...";                            
                            modulesTabs[key][1].textField.setEnabled(false);
                        } else if (isShellConnected === 1) {
                            modulesTabs[key]["shellConnected"]=isShellConnected;
                        }
                        modulesTabs[key][1].panel.setText(listenerTitle);
                        modulesTabs[key][0].tab.setListenerState(isShellConnected);
                    }
                }
            }
        });
    },

    setAllData: function(args){
        var oData = args;
        this.oModulesInfoModel = new sap.ui.model.json.JSONModel();
        this.oModulesInfoModel.setData(oData);
        mainView.setModel(this.oModulesInfoModel);
    },
    
    restoreTabs: function(args){        
        modulesTabs = {};
        //Don't load already loaded tabs
        var tabs = mainView.byId("Main_LogTabsWidget").getItems();
        var openedTabs = [];
        for(var i=0; i<tabs.length; i++){
            openedTabs.push(tabs[i].getText());
        }
        for(var module_name in args){
            if(openedTabs.indexOf(module_name)>=0)
                continue;
            var state = args[module_name].state;
            var logMessage = args[module_name].message;
            mainController.addTab(module_name, ('listener' in args[module_name]));
            modulesTabs[module_name][0].tab.setState(state);
            var logTabLabel = modulesTabs[module_name][0].text;
            logTabLabel.setText(logMessage);
            if(args[module_name].hasOwnProperty("listener")){
                var listener = args[module_name].listener;
                if(listener){
                    var message = listener.message;
                    var isShellConnected = listener.connected;
                    modulesTabs[module_name][1].textView.setValue(message);
                    if (isShellConnected) {
                        if (isShellConnected === 1){
                            modulesTabs[module_name]["shellConnected"]=isShellConnected;
                        } else if (isShellConnected === 2){
                            modulesTabs[module_name]["shellConnected"]=isShellConnected;
                            modulesTabs[module_name][1].textView.toggleStyleClass("listenerDisconnected", isShellConnected);
                        }
                        modulesTabs[module_name][0].tab.setListenerState(isShellConnected);
                    }
                }
            }
        //start logging
        this.serverCommandsHandler.startLog();        
        }
    },

    onListenerMessage: function(args){
        var message = args["message"];
        if (message==="")
            return;
        var view = mainView.byId("Main_ListenerCommandView");
        view.setValue(view.getValue()+"\n"+message);
    },

    showAvailableModules: function(args){
        var oData = args;
        this.oModulesInfoModel = new sap.ui.model.json.JSONModel();
        this.oModulesInfoModel.setData(oData);
        mainView.byId("Main_ModulesTree").setModel(this.oModulesInfoModel);
    },

    showOptions: function(args){
        var dialog =  runDialogView.byId("RunDialog_Dialog");
        var target = mainView.byId("Main_Target").getValue().split(':');
        var host = target[0];
        var port = target[1];        
        //change host and port if available
        for(var index in args){
            if(!args.hasOwnProperty(index))
                continue;
            var entry = args[index];
            if(entry == null)
                continue;
            if(entry["option"].toLowerCase() === "host" && host)
                entry.value.value = host;
            if(entry["option"].toLowerCase() === "port" && port)
                entry.value.value = port;
        }
        oOptionsModel = new sap.ui.model.json.JSONModel();
        oOptionsModel.setData(args);
        dialog.setModel(oOptionsModel);
        dialog.open();
    },

    getSource: function(args) {
        var oData = args;
        var model = new sap.ui.model.json.JSONModel();
        model.setData(oData);
        var dialog = codeEditorDialogView.byId('CodeEditor_Dialog');
        dialog.setModel(model);
        dialog.setTitle(args['module_name']);
        dialog.open();
        codeEditorDialogController.loadEditor();

    },

    onMessageFromServer: function(message){
        this.writeToScreen(message);
    },

    parseAndExecuteMessage: function(message){
        var parsed = JSON.parse(message);
        var command = parsed["command"];
        var args = parsed["args"];
        bind(this.commands[command](args),this);
    },

    showMessageBox: function(message) {
        sap.m.MessageToast.show(message, {
            my: "center center",
            at: "center center",
            duration: 1000
        });
    },
};