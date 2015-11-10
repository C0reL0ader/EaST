sap.ui.controller("mvc.CodeEditor", {
    loadEditor: function(event) {
        var dialog = codeEditorDialogView.byId("CodeEditor_Dialog");
        var message = dialog.getModel().getData()['message'];
        var textArea = document.getElementById('textareaeditor');
        textArea.value = message;
        var editor = CodeMirror.fromTextArea(textArea, {
            lineNumbers: true,
            indentUnit: 4,
            mode: "python"
        });
    },

    saveModule: function(event){
        var newCode = $('.CodeMirror')[0].CodeMirror.getValue();
        var dialog = codeEditorDialogView.byId("CodeEditor_Dialog");
        guiCommandsHandler.saveSource(dialog.getTitle(), newCode);
        dialog.close();
    },

    closeDialog: function(event) {
        var dialog = codeEditorDialogView.byId("CodeEditor_Dialog");
        dialog.close();
    }

});