sap.ui.jsview("mvc.Main", {
    getControllerName: function () {
        return "mvc.Main";
    },
    createContent: function (oController) {

        var mainPanel = new sap.ui.commons.Panel(this.createId("Main_Panel"), {
            title: new sap.ui.core.Title({
                text: "Exploits and Security Tools FRAMEWORK ver. {/version}",
                level: sap.ui.core.TitleLevel.H3
            }),
            height: "100%",
            width: "100%"
        });

        //create a vertical Splitter
        var oSplitterV = new sap.ui.commons.Splitter(this.createId("Main_VerticalSplitter"), {
            splitterOrientation: sap.ui.commons.Orientation.vertical,
            minSizeFirstPane: "20%",
            minSizeSecondPane: "30%",
            height: "90%"
        });
        
        //////////////////////////////
        //Tree widget with available modules
        var oModulesTree = new sap.ui.commons.Tree(this.createId("Main_ModulesTree"), {
            title: "Available modules",
            width: "100%",
            height: "50%"
        });        

        var treeTemplate = new sap.ui.commons.TreeNode({
            text: "{NAME}",
            selectable: "{isFile}",
            icon: "{= ${isFile}? '' : 'sap-icon://folder-blank'}",
            selected: [oController.onTreeNodeSelected, oController],
            toggleOpenState: [oController.onNodeExpanded, treeTemplate],
            expanded: false
        });        

        // speed up expand and collapse animation
        sap.ui.commons.TreeNode.ANIMATION_DURATION = 100;

        //Add mouse dbl click event to template
        treeTemplate.addEventDelegate({
            ondblclick: oController.onTreeNodeDblClick
        }, treeTemplate);
        oModulesTree.bindNodes({name: "nodes", path: "/modules/", template: treeTemplate});


        oModulesTree.addEventDelegate({
            onAfterRendering: function() {
                var nodes = this.getNodes();
                if (!nodes.length)
                    return;
                _.forEach(nodes, function(node){
                    if (node.getExpanded())
                        node.setIcon('sap-icon://open-folder');
                    else
                        node.setIcon("sap-icon://folder-blank");
                });
            }            
        }, oModulesTree);

        var oModuleInfoTextView = new sap.ui.commons.FormattedTextView(this.createId("Main_ModuleInfoTextView"), {
            width: "100%",
            height: "45%",
        });
        var moduleInfoPanel = new sap.ui.commons.Panel({
            height: "50%",
            content: [oModuleInfoTextView],
            showCollapseIcon: false,
            text:"Module info"
        });

        //Create tab widget for log messages of running modules
        var oTabStripWidget = new custom.controls.TabBar(this.createId("Main_LogTabsWidget"), {
            expandable: false,
            header: new custom.controls.TabBarHeader({
                close: oController.onTabClose
            }),
            stretchContentHeight: true
        });

        var tabsPanel = new sap.ui.commons.Panel({
            height: "100%",
            content: [oTabStripWidget],
            showCollapseIcon: false,
            text:"Running modules"
        })

        //HEADER TOOLBAR
        var reconnectButton = new sap.m.Button(this.createId("Main_ReconnectButton"), {
            text: "Reconnect",
            press: oController.reconnect
        });

        var separator = new sap.m.Label({width:"50px"});
        var targetLabel = new sap.m.Label({text: "Target:"});

        var targetTextBox = new sap.m.Input(this.createId("Main_Target"), {
            width: "200px",
            height: "100%",
            value: "127.0.0.1:80"
        });

        var headerToolar = new sap.m.Bar({
            contentLeft: [reconnectButton, separator, targetLabel, targetTextBox],
            design: sap.m.BarDesign.Footer
        });

        var searchTextBox = new sap.m.SearchField(this.createId("SearchTextBox"), {
            width: "200px",
            placeholder: "Type to search module...",
            liveChange: [oController.searchModules, searchTextBox]
        });
        searchTextBox.setPlaceholder();        

        var editorBtn = new sap.m.Button({
            icon: 'sap-icon://edit',
            press: oController.openEditor,
            tooltip: "Edit selected module"
        });

        var runModuleBtn = new sap.m.Button({
            icon: 'sap-icon://media-play',
            press: oController.onTreeNodeDblClick,
            tooltip: "Run selected module"
        });

        var subHeaderToolbar = new sap.m.Bar(this.createId("Main_Toolbar"), {
            contentLeft: [searchTextBox, runModuleBtn, editorBtn],
            design: sap.m.BarDesign.Header
        });
        

        mainPanel.addContent(headerToolar);
        mainPanel.addContent(subHeaderToolbar);
        mainPanel.addContent(oSplitterV);

        oSplitterV.addFirstPaneContent(oModulesTree);
        oSplitterV.addFirstPaneContent(moduleInfoPanel);
        oSplitterV.addSecondPaneContent(tabsPanel);
        return mainPanel;

    },
});
