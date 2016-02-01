sap.m.IconTabBar.extend("custom.controls.TabBar",{
    metadata:{
        aggregations:{
            header:  {type:"sap.m.IconTabHeader", multiple : false}
        },
    },

    _getIconTabHeader: function(){
        var oControl = this.getAggregation("header");

        if (!oControl) {
            oControl = new sap.m.IconTabHeader(this.getId() + "--header", {});
            this.setAggregation("_header", oControl, true);
        }
        return oControl;
    },

    renderer: {}
});


sap.m.IconTabHeader.extend("custom.controls.TabBarHeader", {
    metadata: {
        events: {
            "close": {}
        },
    },

    onclick: function(e){
        var oSource = e.target;
        if (oSource.className == "tabFilterCloseBtn") {
            //find the items index
            var iIdx = this.getItemIndex(jQuery(oSource).parentByAttribute("id"));
            if (iIdx > -1) {
                var tab = this.getItems()[iIdx];
                var tabName = tab.getText();
                //remove content of tab
                tab.removeAllContent();
                //and remove tab from header
                this.removeItem(tab);
                //fire close event
                this.fireClose({index:iIdx, name: tabName});
                //
                var count = this.getItems().length;
                if (count > 0){
                    this.setSelectedItem(this.getItems()[iIdx]);
                }
                if (count == iIdx){
                    this.setSelectedItem(this.getItems()[iIdx-1]);
                }
            }
            return;
        }
    },

    getItemIndex: function(oDomRef) {
        var sId;
        if (!oDomRef.id || oDomRef.id.search("-text") != -1) {
            // icon or close button
            var oItemDomRef = jQuery(oDomRef).parentByAttribute("id");
            sId = oItemDomRef.id;
        } else {
            sId = oDomRef.id;
        }

        for (var idx = 0, aTabs = this.getItems(); idx < aTabs.length; idx++) {
            if (sId == aTabs[idx].getId()) {
                return idx;
            }
        }
        return -1;
    },

    renderer: function(oRM, oControl){
        // return immediately if control is not visible
        if (!oControl.getVisible()) {
            return;
        }

        var aItems = oControl.getItems(),
            bTextOnly = oControl._checkTextOnly(aItems),
            bNoText = oControl._checkNoText(aItems),
            oResourceBundle = sap.ui.getCore().getLibraryResourceBundle('sap.m');

        var oIconTabBar = oControl.getParent();
        var bUpperCase = oIconTabBar && oIconTabBar instanceof sap.m.IconTabBar && oIconTabBar.getUpperCase();

        // render wrapper div
        oRM.write("<div role='tablist' ");
        oRM.addClass("sapMITH");
        if (oControl._scrollable) {
            oRM.addClass("sapMITBScrollable");
            if (oControl._bPreviousScrollForward) {
                oRM.addClass("sapMITBScrollForward");
            } else {
                oRM.addClass("sapMITBNoScrollForward");
            }
            if (oControl._bPreviousScrollBack) {
                oRM.addClass("sapMITBScrollBack");
            } else {
                oRM.addClass("sapMITBNoScrollBack");
            }
        } else {
            oRM.addClass("sapMITBNotScrollable");
        }
        // Check for upperCase property on IconTabBar
        if (bUpperCase) {
            oRM.addClass("sapMITBTextUpperCase");
        }
        oRM.writeControlData(oControl);
        oRM.writeClasses();
        oRM.write(">");

        // render left scroll arrow
        oRM.renderControl(oControl._getScrollingArrow("left"));

        // render scroll container on touch devices
        if (oControl._bDoScroll) {
            oRM.write("<div id='" + oControl.getId() + "-scrollContainer' class='sapMITBScrollContainer'>");
        }

        oRM.write("<div id='" + oControl.getId() + "-head'");
        oRM.addClass("sapMITBHead");

        if (bTextOnly) {
            oRM.addClass("sapMITBTextOnly");
        }

        if (bNoText) {
            oRM.addClass("sapMITBNoText");
        }

        oRM.writeClasses();
        oRM.write(">");

        jQuery.each(aItems, function(iIndex, oItem) {
            if (!(oItem instanceof sap.m.IconTabSeparator) && !oItem.getVisible()) {
                return; // only render visible items
            }

            var sTabParams = '';

            if (oItem instanceof sap.m.IconTabSeparator) {
                if (oItem.getIcon()) {
                    sTabParams += 'role="img" aria-label="' + oResourceBundle.getText("ICONTABBAR_NEXTSTEP") + '"';
                } else {
                    sTabParams += 'role="separator"';
                }
            } else {
                sTabParams += 'role="tab" aria-controls="' + oControl.getParent().sId + '-content" ';

                //if there is tab text
                if (oItem) {
                    var sIconColor = oItem.getIconColor();
                    var bReadIconColor = sIconColor === 'Positive' || sIconColor === 'Critical' || sIconColor === 'Negative';

                    if (oItem.getText().length || oItem.getCount() !== "" || oItem.getIcon()) {
                        sTabParams += 'aria-labelledby="';
                        var aIds = [];

                        if (oItem.getText().length) {
                            aIds.push(oItem.getId() + '-text');
                        }
                        if (oItem.getCount() !== "") {
                            aIds.push(oItem.getId() + '-count');
                        }
                        if (oItem.getIcon()) {
                            aIds.push(oItem.getId() + '-icon');
                        }
                        if (bReadIconColor) {
                            aIds.push(oItem.getId() + '-iconColor');
                        }

                        sTabParams += aIds.join(' ');
                        sTabParams += '"';
                    }
                }
            }

            oRM.write('<div ' + sTabParams + ' ');

            oRM.writeElementData(oItem);
            oRM.addClass("sapMITBItem");

            if (oItem instanceof sap.m.IconTabFilter) {

                if (oItem.getDesign() === sap.m.IconTabFilterDesign.Vertical) {
                    oRM.addClass("sapMITBVertical");
                } else if (oItem.getDesign() === sap.m.IconTabFilterDesign.Horizontal) {
                    oRM.addClass("sapMITBHorizontal");
                }

                if (oItem.getShowAll()) {
                    oRM.addClass("sapMITBAll");
                } else {
                    oRM.addClass("sapMITBFilter");
                    oRM.addClass("sapMITBFilter" + oItem.getIconColor());
                }

                if (!oItem.getEnabled()) {
                    oRM.addClass("sapMITBDisabled");
                }

                var sTooltip = oItem.getTooltip_AsString();
                if (sTooltip) {
                    oRM.writeAttributeEscaped("title", sTooltip);
                }

                oRM.writeClasses();
                oRM.write(">");
                oRM.write("<div id='" + oItem.getId() + "-listener' class=''>");

                if (!oItem.getShowAll() || !oItem.getIcon()) {
                    if (bReadIconColor) {
                        oRM.write('<div id="' + oItem.getId() + '-iconColor" style="display: none;">' + oResourceBundle.getText('ICONTABBAR_ICONCOLOR_' + sIconColor.toUpperCase()) + '</div>');
                    }

                    oRM.renderControl(oItem._getImageControl(['sapMITBFilterIcon', 'sapMITBFilter' + oItem.getIconColor()],
                        oControl, ['sapMITBFilterCritical', 'sapMITBFilterPositive', 'sapMITBFilterNegative', 'sapMITBFilterDefault']));
                }

                if (!oItem.getShowAll() && !oItem.getIcon() && !bTextOnly)  {
                    oRM.write("<span class='sapMITBFilterNoIcon'> </span>");
                }

                if (oItem.getDesign() === sap.m.IconTabFilterDesign.Horizontal) {
                    oRM.write("</div>");
                    oRM.write("<div class='sapMITBHorizontalWrapper'>");
                }

                //�������� �� �����

                /*oRM.write("<span id='" + oItem.getId() + "-count' ");
                oRM.addClass("sapMITBCount");
                oRM.writeClasses();
                oRM.write(">");*/

                if ((oItem.getCount() === "") && (oItem.getDesign() === sap.m.IconTabFilterDesign.Horizontal)) {
                    //this is needed for the correct placement of the text in the horizontal design
                    oRM.write("&nbsp;");
                } else {
                    oRM.writeEscaped(oItem.getCount());
                }

                oRM.write("</span>");

                if (oItem.getDesign() === sap.m.IconTabFilterDesign.Vertical) {
                    oRM.write("</div>");
                }

                if (oItem.getText().length) {
                    oRM.write("<div id='" + oItem.getId() + "-text' ");
                    oRM.addClass("sapMITBText");
                    // Check for upperCase property on IconTabBar
                    if (bUpperCase) {
                        oRM.addClass("sapMITBTextUpperCase");
                    }
                    if (oItem.getState()!=null){
                        if(oItem.getState())
                            oRM.addClass("moduleSucceeded");
                        else
                            oRM.addClass("moduleFailed");
                    }
                    oRM.writeClasses();
                    oRM.write(">");
                    if (oItem.isListenerUsed()) {
                        oRM.write("<div id='"+ oItem.getId()+"-listener'");
                        oRM.addClass('listenerLabel');
                        if(oItem.getListenerState()===1)
                            oRM.addClass("moduleSucceeded");
                        else if(oItem.getListenerState()===2)
                            oRM.addClass("moduleFailed");
                        oRM.writeClasses();
                        oRM.write("></div>");
                    }
                    oRM.writeEscaped(oItem.getText());
                    oRM.write("<button class='tabFilterCloseBtn'>x</button>");
                    oRM.write("</div>");
                }

                if (oItem.getDesign() === sap.m.IconTabFilterDesign.Horizontal) {
                    oRM.write("</div>");
                }

                oRM.write("<div class='sapMITBContentArrow'></div>");

            } else { // separator
                oRM.addClass("sapMITBSep");

                if (!oItem.getIcon()) {
                    oRM.addClass("sapMITBSepLine");
                }
                oRM.writeClasses();
                oRM.write(">");

                if (oItem.getIcon()) {
                    oRM.renderControl(oItem._getImageControl(['sapMITBSepIcon'], oControl));
                }
            }
            oRM.write("</div>");
        });

        oRM.write("</div>");

        if (oControl._bDoScroll) {
            oRM.write("</div>"); //scrollContainer
        }

        // render right scroll arrow
        oRM.renderControl(oControl._getScrollingArrow("right"));

        // end wrapper div
        oRM.write("</div>");
    }
});

sap.m.IconTabFilter.extend("custom.controls.Tab", {
    metadata:{
        properties:{
            useListener: {type: "boolean"},
            _state: {type: "boolean"},
            _listenerState: {type: "int"},
        }
    },

    setState: function(state){
        if(typeof state == "boolean"){
            this.setProperty("_state", state, true);
            var id = this.getId();
            if (!state) {
                this.$().find('#' + id + "-text").toggleClass("moduleFailed", true);
            }
            else{
                this.$().find('#'+id+"-text").toggleClass("moduleSucceeded", true);
            }
        }
    },

    setListenerState: function(state) {
        this.setProperty("_listenerState", state, 0);
        var id = this.getId();
        if (state===1) {
            this.$().find('#' + id + "-listener").toggleClass("moduleSucceeded", true);
            this.$().find('#'+id+"-listener").toggleClass("moduleFailed", false);
        }
        else if (state == 2){
            this.$().find('#'+id+"-listener").toggleClass("moduleFailed", true);
            this.$().find('#' + id + "-listener").toggleClass("moduleSucceeded", false);
        }
        else {
            this.$().find('#'+id+"-listener").toggleClass("moduleFailed", false);
            this.$().find('#' + id + "-listener").toggleClass("moduleSucceeded", false);    
        }
        this.rerender();
    },

    getState: function(){
        return this.getProperty("_state");
    },

    getListenerState: function() {
        return this.getProperty("_listenerState");
    },

    isListenerUsed: function() {
        return this.getProperty("useListener");
    }
})