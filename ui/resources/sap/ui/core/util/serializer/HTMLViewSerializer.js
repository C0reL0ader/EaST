/*
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','sap/ui/base/EventProvider','./delegate/HTML','sap/ui/thirdparty/vkbeautify'],function(q,E,H,v){"use strict";var a=E.extend("sap.ui.core.util.serializer.HTMLViewSerializer",{constructor:function(V,w,g,G){E.apply(this);this._oView=V;this._oWindow=w;this._fnGetControlId=g;this._fnGetEventHandlerName=G;}});a.prototype.serialize=function(){var s=function(C){return(C instanceof this._oWindow.sap.ui.core.mvc.View);};var c=new sap.ui.core.util.serializer.Serializer(this._oView,new H(this._fnGetControlId,this._fnGetEventHandlerName),true,this._oWindow,s);var r=c.serialize();var V=[];V.push('<template');if(this._oView.getControllerName&&this._oView.getControllerName()){V.push(' data-controller-name="'+this._oView.getControllerName()+'"');}V.push(" >");V.push(r);V.push("</template>");return vkbeautify.xml(V.join(""));};return a;},true);
