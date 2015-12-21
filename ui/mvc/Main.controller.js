sap.ui.controller("mvc.Main", {
	
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
		var indexOfCtrl = 0;
		var description = event.oSource.getBindingContext().getProperty('DESCRIPTION') || "n/a";
		var vendor = event.oSource.getBindingContext().getProperty('VENDOR');		
		var cve = event.oSource.getBindingContext().getProperty('CVE Name');
		var downlink = event.oSource.getBindingContext().getProperty('DOWNLOAD_LINK');
		var notes = event.oSource.getBindingContext().getProperty('NOTES') || "n/a";
		var links = event.oSource.getBindingContext().getProperty('LINKS');
		var vendorText  = "n/a";
		var cveText = "n/a";
		var downlinkText = "n/a";
		var linkText = "n/a";

		if (vendor) {
			if (vendor.trim().toLowerCase().startsWith('http')) {
				var oLink = new sap.ui.commons.Link("vendor_", {
					text: vendor,
					href: vendor,
					target: "_blank"
				});
				infoTextControl.addControl(oLink);
				vendorText = '<embed data-index=\"'+indexOfCtrl+'\" />';
				indexOfCtrl += 1;
			}
			else {
				vendorText = vendor;
			}
		}
		if (cve) {
			var oLink = new sap.ui.commons.Link("cve_", {
				text: cve,
				href: "https://www.google.ru/search?q="+cve,
				target: "_blank"
			});
			infoTextControl.addControl(oLink);
			cveText = '<embed data-index=\"'+indexOfCtrl+'\" />';
			indexOfCtrl += 1;
		}
		if (downlink) {
			oLink = new sap.ui.commons.Link("dl_", {
				text: downlink,
				href: downlink,
				target: "_blank"
			});
			infoTextControl.addControl(oLink);
			indexOfCtrl += 1;
		}
		if (links) {
			if ($.isArray(links)) {
				linkText = "";
				links.forEach(function(el, index) {
					oLink = new sap.ui.commons.Link("link_"+index, {
						text: el,
						href: el,
						target: "_blank"
					});
					linkText += '<embed data-index=\"'+ indexOfCtrl +'\" />,  ';
					infoTextControl.addControl(oLink);
					indexOfCtrl += 1;
				});
			}
			else {
				oLink = new sap.ui.commons.Link("link_"+0, {
					text: links,
					href: links,
					target: "_blank"
				});
				infoTextControl.addControl(oLink);
				linkText += '<embed data-index=\"'+ indexOfCtrl +'\" />';
			}
		}		

		var text = "<strong>Description:</strong> " + description + "<br>";
        text += "<strong>Vendor:</strong> " + vendorText + "<br>";
        text += "<strong>CVE Name:</strong> " + cveText + "<br>";
        text += "<strong>Download link:</strong> " + downlinkText + "<br>";
        text += "<strong>Links:</strong> " + linkText + "<br>";
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
		var textToSearch = event.getParameters().newValue;		
		var oModulesTree = mainView.byId("Main_ModulesTree");
		var binding = oModulesTree.getBinding("nodes");
		if (!textToSearch){
			binding.filter([]);
			return;
		}
		var oNameFilter = new sap.ui.model.Filter("NAME", "Contains", textToSearch);
		var oDescFilter = new sap.ui.model.Filter("DESCRIPTION", "Contains", textToSearch);
		var oCveFilter = new sap.ui.model.Filter("CVE Name", "Contains", textToSearch);
		var oVendorFilter = new sap.ui.model.Filter("VENDOR", "Contains", textToSearch);

		var oFileFilter = new sap.ui.model.Filter("isFile", sap.ui.model.FilterOperator.EQ, true);
		var orFilter = new sap.ui.model.Filter([oNameFilter, oCveFilter, oDescFilter, oVendorFilter]);
		binding.filter([orFilter, oFileFilter]);
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