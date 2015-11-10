/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(["jquery.sap.global"],function(q){"use strict";var I={};I.render=function(r,c){var i=sap.ui.core.IconPool.getIconInfo(c.getSrc()),w=c.getWidth(),h=c.getHeight(),C=c.getColor(),b=c.getBackgroundColor(),s=c.getSize(),t=c.getTooltip_AsString();r.write("<span");r.writeControlData(c);if(!c.getDecorative()){r.writeAttribute("tabindex",0);}if(t){r.writeAttributeEscaped("title",t);}if(i){r.writeAttribute("data-sap-ui-icon-content",i.content);r.writeAttribute("role","img");r.writeAttributeEscaped("aria-label",t||i.name);r.addStyle("font-family","'"+i.fontFamily+"'");}if(w){r.addStyle("width",w);}if(h){r.addStyle("height",h);r.addStyle("line-height",h);}if(!(C in sap.ui.core.IconColor)){r.addStyle("color",C);}if(!(b in sap.ui.core.IconColor)){r.addStyle("background-color",b);}if(s){r.addStyle("font-size",s);}r.addClass("sapUiIcon");if(i&&!i.suppressMirroring){r.addClass("sapUiIconMirrorInRTL");}r.writeClasses();r.writeStyles();r.write("></span>");};return I;},true);
