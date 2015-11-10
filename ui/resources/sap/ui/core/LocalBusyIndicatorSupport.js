/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','./Element'],function(q,E){"use strict";var L=function(){if(this===sap.ui.core.Control.prototype){this.setDelay=function(d){this.setBusyIndicatorDelay(d);};}else{q.sap.log.error("Only controls can use the LocalBusyIndicator",this);}};return L;},true);
