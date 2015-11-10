/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','./Date'],function(q,D){"use strict";var a=D.extend("sap.ui.model.type.DateTime",{constructor:function(){D.apply(this,arguments);this.sName="DateTime";}});a.prototype._createFormats=function(){this.oOutputFormat=sap.ui.core.format.DateFormat.getDateTimeInstance(this.oFormatOptions);if(this.oFormatOptions.source){this.oInputFormat=sap.ui.core.format.DateFormat.getDateTimeInstance(this.oFormatOptions.source);}};return a;},true);
