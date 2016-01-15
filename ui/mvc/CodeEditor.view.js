sap.ui.jsview("mvc.CodeEditor", {

    getControllerName : function() {
        return "mvc.CodeEditor";
    },

    createContent : function(oController) {
        var htmlControl = new sap.ui.core.HTML(this.createId('CodeEditor_Editor'), {
            content: '<textarea id="textareaeditor"></textarea>'
        });

        var dialog =  new sap.ui.commons.Dialog(this.createId("CodeEditor_Dialog"), {
            modal: true,
            width: '800px',
            height: '600px',
            buttons: [new sap.ui.commons.Button({
                text:"Save",
                press: [oController.saveModule, dialog]
            }),
                new sap.ui.commons.Button({
                    text:"Cancel",
                    press: [oController.closeDialog, dialog]
                }),
            ],
            content:[htmlControl],
        });
        return dialog;
    },

});
