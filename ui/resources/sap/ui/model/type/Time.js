/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','./Date'],function(q,D){"use strict";var T=D.extend("sap.ui.model.type.Time",{constructor:function(){D.apply(this,arguments);this.sName="Time";}});T.prototype._createFormats=function(){this.oOutputFormat=sap.ui.core.format.DateFormat.getTimeInstance(this.oFormatOptions);if(this.oFormatOptions.source){this.oInputFormat=sap.ui.core.format.DateFormat.getTimeInstance(this.oFormatOptions.source);}};return T;},true);
