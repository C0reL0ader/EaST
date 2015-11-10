/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global'],function(q){"use strict";var R={};R.extend=function(p){var c={_super:p};for(var f in p){if(typeof(p[f])=="function"){c[f]=(function(){var m=f;return function(){return c._super[m].apply(this,arguments);};}());}}return c;};R.getTextAlign=function(t,T){var s="";var c=sap.ui.getCore().getConfiguration();switch(t){case sap.ui.core.TextAlign.End:switch(T){case"LTR":s="right";break;case"RTL":s="left";break;default:if(c.getRTL()){s="left";}else{s="right";}break;}break;case sap.ui.core.TextAlign.Begin:switch(T){case"LTR":s="left";break;case"RTL":s="right";break;default:if(c.getRTL()){s="right";}else{s="left";}break;}break;case sap.ui.core.TextAlign.Right:if(c.getRTL()){if(T=="LTR"){s="right";}}else{s="right";}break;case sap.ui.core.TextAlign.Center:s="center";break;case sap.ui.core.TextAlign.Left:if(c.getRTL()){s="left";}else{if(T=="RTL"){s="left";}}break;}return s;};return R;},true);
