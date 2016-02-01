var MessagesController = function() {
    this.timeout = 4000;
    this.container = new sap.ui.layout.VerticalLayout({width: "auto"});
    this.popup = new sap.ui.core.Popup(this.container, false, true, true);
    this.popup.attachClosed(function() {
        messageController.container.destroyContent();
    })
    this.timer = 0;
};

MessagesController.prototype = {
    show: function() {
        messageController.popup.open(500,sap.ui.core.Popup.Dock.EndBottom, sap.ui.core.Popup.Dock.EndBottom);
        messageController.timer = setTimeout(function() {
            messageController.popup.close(500);
        }, messageController.timeout);
    },

    addMessage: function(sMessage, sType) {
        var label = messageController.createMessageItem(sMessage, sType);
        messageController.container.insertContent(label, 0);
        if (messageController.popup.isOpen()){
            clearTimeout(messageController.timer);
            messageController.timer = setTimeout(function () {
                messageController.popup.close(500);
            }, messageController.timeout);
        }
        else {
            messageController.show();
        }
    },

    createMessageItem: function(sMessage, sType) {
        var msgClass;
        if (sType === "info"){
            msgClass = "moduleSucceeded"
        }
        else {
            msgClass = "moduleFailed"
        }
        content = "<div class='msgItem "+ msgClass +"' onclick='messageController.popup.close(500)'><b>"+ sMessage+"</b></div>";
        control = new sap.ui.core.HTML({content: content});
        return control;
    },

    addInfoMessage: function (sMessage) {
        messageController.addMessage(sMessage, "info");
    },

    addErrorMessage: function (sMessage) {
        messageController.addMessage(sMessage, "error");
    }

};