sap.ui.jsview("mvc.RunDialog", {

    getControllerName : function() {
        return "mvc.RunDialog";
    },

    createContent : function(oController) {
        var enableListenerCheckBox = new sap.ui.commons.CheckBox(this.createId("RunDialog_ListenerCheckBox"), {
            text: "Enable listener for module",
            width: "100%",
            editable: true,
            change: oController.enableListenerPort
        });

        var vListenerLayout = new sap.ui.layout.VerticalLayout({
            width: '100%',
            content: [enableListenerCheckBox]
        });
        var divider = new sap.ui.commons.HorizontalDivider();
        var oMatrixLayout = new sap.ui.commons.layout.MatrixLayout(this.createId("RunDialog_MatrixLayout"),{
            layoutFixed: false,
            width:"auto",
            widths:["auto", "100%"]
        });
        oMatrixLayout.bindAggregation("rows", "/", function(sId, oContext){
            var type = oContext.getProperty("value/type");
            var control;
            if (type === 'list'){
                control = new sap.ui.commons.DropdownBox({
                    selectedKey: "{value/selected}",
                    width: "100%"
                });
                control.bindAggregation("items", "value/options/", function(sId, oContext){
                    return new sap.ui.core.ListItem({text: "{}", key: "{}"})
                });
            }
            else if (type === 'bool') {
                control = new sap.ui.commons.CheckBox({
                    checked: '{value/value}',
                    change: function() {
                        this.rerender();
                    }
                });
            }
            else {
                control = new sap.ui.commons.TextField({
                    value: '{value/value}',
                    width: '100%'
                });
            }

            return new sap.ui.commons.layout.MatrixLayoutRow({
                cells: [
                    new sap.ui.commons.layout.MatrixLayoutCell({
                        content: new sap.ui.commons.Label({text:"{option}:", width: "100%"})
                    }),
                    new sap.ui.commons.layout.MatrixLayoutCell({
                        content: control
                    })
                ]
            });
        });

        var dialog =  new sap.ui.commons.Dialog(this.createId("RunDialog_Dialog"), {
            modal: true,
            buttons: [new sap.ui.commons.Button({
                text:"Run",
                press: [oController.runModule, dialog]
            }),
                new sap.ui.commons.Button({
                    text:"Cancel",
                    press: [oController.closeDialog, dialog]
                }),
            ],
            width: "30%",
            content:[vListenerLayout, divider, oMatrixLayout]
        });
        return dialog;
    },

    bind: function(func, context) {
        return function() {
            return func.apply(context, arguments);
        };
    }

});
