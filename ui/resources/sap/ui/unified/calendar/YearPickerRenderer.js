/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global'],function(q){"use strict";var Y={};Y.render=function(r,y){var t=y.getTooltip_AsString();var I=y.getId();var c=y.getYear();r.write("<div");r.writeControlData(y);r.addClass("sapUiCalYearPicker");r.writeClasses();if(t){r.writeAttributeEscaped('title',t);}r.writeAccessibilityState(y,{role:"grid",readonly:"true",multiselectable:"false"});r.write(">");var a=c-10;if(a>=9980){a=9980;}else if(a<1){a=1;}for(var i=0;i<20;i++){if(i==0||i%y._iColumns==0){r.write("<div");r.writeAccessibilityState(null,{role:"row"});r.write(">");}r.write("<div");r.writeAttribute("id",I+"-y"+a);r.addClass("sapUiCalYear");if(a==c){r.addClass("sapUiCalYearSel");}r.writeAttribute("tabindex","-1");r.writeClasses();r.writeAccessibilityState(null,{role:"gridcell"});r.write(">");r.write(a);r.write("</div>");a++;if((i+1)%y._iColumns==0){r.write("</div>");}}r.write("</div>");};return Y;},true);
