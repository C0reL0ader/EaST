sap.ui.controller("mvc.Main", {

	/**
	 * Called when a controller is instantiated and its View controls (if
	 * available) are already created. Can be used to modify the View before it
	 * is displayed, to bind event handlers and do other one-time
	 * initialization.
	 *
	 */
	// onInit: function() {
	//
	// },
	/**
	 * Similar to onAfterRendering, but this hook is invoked before the
	 * controller's View is re-rendered (NOT before the first rendering!
	 * onInit() is used for that one!).
	 *
	 */
	// onBeforeRendering: function() {
	//
	// },
	/**
	 * Called when the View has been rendered (so its HTML is part of the
	 * document). Post-rendering manipulations of the HTML could be done here.
	 * This hook is the same one that SAPUI5 controls get after being rendered.
	 *
	 */
	// onAfterRendering: function() {
	//
	// },
	/**
	 * Called when the Controller is destroyed. Use this one to free resources
	 * and finalize activities.
	 *
	 */
	// onExit: function() {
	//
	// }
	onTabClose: function(oEvent){
		var tabName = oEvent.getParameter("name");
		guiCommandsHandler.killProcess(tabName);
	},

	reconnect: function(){
		websocketHandler.reconnect();
	},

	onTreeNodeSelected: function(event){
		var infoTextControl = mainView.byId("Main_ModuleInfoTextView");
		infoTextControl.destroyControls();
		var description = event.oSource.getBindingContext().getProperty('DESCRIPTION') || "n/a";
		var vendor = event.oSource.getBindingContext().getProperty('VENDOR') || "n/a";
		var cve = event.oSource.getBindingContext().getProperty('CVE Name') || "n/a";
		var downlink = event.oSource.getBindingContext().getProperty('DOWNLOAD_LINK') || "n/a";
		var notes = event.oSource.getBindingContext().getProperty('NOTES') || "n/a";
		var links = event.oSource.getBindingContext().getProperty('LINKS');
		var oLink = new sap.ui.commons.Link("cve_", {
			text: cve,
			href: "https://www.google.ru/search?q="+cve,
			target: "_blank"
		});
		infoTextControl.addControl(oLink);
		oLink = new sap.ui.commons.Link("dl_", {
			text: downlink,
			href: downlink,
			target: "_blank"
		});
		infoTextControl.addControl(oLink);		

		var embedLinks = "";
		if ($.isArray(links)) {
			links.forEach(function(el, index) {
				oLink = new sap.ui.commons.Link("link_"+index, {
					text: el,
					href: el,
					target: "_blank"
				});
				embedLinks += '<embed data-index=\"'+(index+2)+'\" />,  ';
				infoTextControl.addControl(oLink);
			});
		}
		else {
			oLink = new sap.ui.commons.Link("link_"+0, {
				text: links,
				href: links,
				target: "_blank"
			});
			infoTextControl.addControl(oLink);
			embedLinks += '<embed data-index=\"2\" />';
		}


		var text = "<strong>Description:</strong> " + description + "<br>";
        text += "<strong>Vendor:</strong> " + vendor + "<br>";
        text += "<strong>CVE Name:</strong> <embed data-index=\"0\" /><br>";
        text += "<strong>Download link:</strong> <embed data-index=\"1\" /><br>";
        text += "<strong>Links:</strong> " +embedLinks+ "<br>";
        text += "<strong>Notes:</strong> " + notes + "<br>";
		infoTextControl.setHtmlText(text);
	},

	onNodeExpanded: function(oEvent) {
		if (!this.getExpanded())
            this.setIcon('sap-icon://open-folder');
        else
            this.setIcon("sap-icon://folder-blank");
	},
	
	addTab: function (tab_name, use_listener){
		var tabContentTextView = new sap.m.Text({text:"Starting...", height:'50%'});
		var panel = new sap.ui.commons.Panel({
			height: '50%',
			width: '100%',
			text: 'Log:',
			content: [tabContentTextView]
		});
		var tab = new custom.controls.Tab({text: tab_name, height: '100%', useListener: use_listener});
		tab.addContent(panel);
		var oTabStripWidget = mainView.byId("Main_LogTabsWidget");
		modulesTabs[tab_name] = [{text: tabContentTextView, tab: tab, panel:panel}];
		oTabStripWidget.addItem(tab);
		oTabStripWidget.setSelectedItem(tab);
		if(use_listener){
			var listenerPanel = mainController.createListenerTemplate(tab_name);
			tab.addContent(listenerPanel.panel);
			modulesTabs[tab_name].push(listenerPanel);
		}
	},

	searchModules: function(event){
		var textToSearch = event.getParameters().value;		
		var oModulesTree = mainView.byId("Main_ModulesTree");
		var binding = oModulesTree.getBinding("nodes");
		if (!textToSearch){
			binding.filter([]);
			return;
		}
		var oFilter = new sap.ui.model.Filter("NAME", "Contains", textToSearch);
		var oFileFilter = new sap.ui.model.Filter("isFile", sap.ui.model.FilterOperator.EQ, true);
		binding.filter([oFilter, oFileFilter]);
		if(textToSearch)
			oModulesTree.expandAll();
	},
    
    setConnectionState: function(state){
        var connectButton = mainView.byId("Main_ReconnectButton");
        if (state){
            connectButton.setType(sap.m.ButtonType.Accept);
            connectButton.setText("Connected");
            connectButton.setTooltip("GUI connected to server");
        } else {
            connectButton.setType(sap.m.ButtonType.Reject);
            connectButton.setText("Reconnect");
            connectButton.setTooltip("Try to reconnect to server");
        }
    },

	sendListenerCommand: function(event){
		var command = event.getParameters().newValue;
		this.setValue("");
		var module_name = this.data('module_name');
		guiCommandsHandler.sendListenerCommand(module_name, command, window.doSend);
	},

	startListener: function (event) {
		var listenerButton = mainView.byId("Main_ListenerButton");
		guiCommandsHandler.startListener(window.doSend);
		listenerButton.setText("Stop listener");
		listenerButton.setType(sap.m.ButtonType.Accept);
	},

	createListenerTemplate: function(module_name){
		//LISTENER PANEL
		var listenerPanel = new sap.ui.commons.Panel({
			height: "50%",
			width:"100%",
			text: "Listener",
			areaDesign: sap.ui.commons.enums.AreaDesign.Plain
		});

		var listenerCommandView = new sap.ui.commons.TextArea({
			width: "100%",
			height: "90%",
			editable: false
		});
		listenerCommandView.addStyleClass("moduleInfoTextView");

		var listenerCommandField = new sap.ui.commons.TextField({
			height: "10%",
			width: "100%",
			placeholder:"Enter commands here...",
			change: [mainController.sendListenerCommand, listenerCommandField]
		});
		listenerCommandField.data('module_name', module_name);
		listenerPanel.addContent(listenerCommandView);
		listenerPanel.addContent(listenerCommandField);
		return {panel: listenerPanel, textView: listenerCommandView, textField: listenerCommandField};
	},

	scrollToBottom: function(event){
		arguments = $(this);
		alert(1);
	},

	onTreeNodeDblClick: function(oEvent){
		if (oEvent.type == 'dblclick' && !this.getSelectable())
			return;
		var nodes = mainController.getSelectedNodes('You should select module to run');
		if (nodes.length <= 0 || !nodes[0].getSelectable())
			return;
		var dialog = runDialogView.byId("RunDialog_Dialog");
		dialog.setTitle(nodes[0].getText());
		guiCommandsHandler.showOptions(nodes[0].getText(), doSend);
	},

	openEditor: function(event) {
		var nodes = mainController.getSelectedNodes('You should select module to edit');
		if(nodes.length <= 0)
			return;
		guiCommandsHandler.getSource(nodes[0].getText());
	},

	getSelectedNodes: function(warnMessage) {
		var oTree = mainView.byId('Main_ModulesTree');
		_checkedNodes = [];

		oTree.getNodes().forEach(function(node){
			if(node.getIsSelected()) _checkedNodes.push(node);
			mainController._getCheckedSubNodes(node);
		});
		if(_checkedNodes.length <= 0){
			sap.m.MessageToast.show(warnMessage, {
				my: "center center",
				at: "center center",
				duration: 1000
			});
		}
		return _checkedNodes;
	},

	_getCheckedSubNodes: function(node){
		node.getNodes().forEach(function(subNode){
			if(subNode.getIsSelected()) _checkedNodes.push(subNode);
			mainController._getCheckedSubNodes(subNode);
		});
	}

});