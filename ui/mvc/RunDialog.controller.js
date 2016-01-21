sap.ui.controller("mvc.RunDialog", {

    runModule: function(){
        var dialog = runDialogView.byId("RunDialog_Dialog");
        var listenerCheckBox = runDialogView.byId("RunDialog_ListenerCheckBox");
        var isListenerEnabled = listenerCheckBox.getChecked();
        var data = oOptionsModel.getData();
        var args = {
            module_name: dialog.getTitle(),
            use_listener: isListenerEnabled,
            options: data
        };
        guiCommandsHandler.startModule(args, mainController.addModuleTab);
        dialog.close();
    },

    closeDialog: function(evt, data){
        var dialog = runDialogView.byId("RunDialog_Dialog");
        dialog.close();
    },

    enableListenerPort: function(evt){
        var checkBox = evt.oSource;
        checkBox.rerender();
    }

});