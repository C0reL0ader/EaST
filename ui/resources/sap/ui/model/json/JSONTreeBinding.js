/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','sap/ui/model/ClientTreeBinding'],function(q,C){"use strict";var J=C.extend("sap.ui.model.json.JSONTreeBinding");J.prototype.getNodeContexts=function(c,s,l){if(!s){s=0;}if(!l){l=this.oModel.iSizeLimit;}var a=c.getPath();if(!q.sap.endsWith(a,"/")){a=a+"/";}if(!q.sap.startsWith(a,"/")){a="/"+a;}var b=[],t=this,n=this.oModel._getObject(a),A=this.mParameters&&this.mParameters.arrayNames,d;if(n){if(A&&q.isArray(A)){q.each(A,function(i,e){d=n[e];if(d){q.each(d,function(S,o){t._saveSubContext(o,b,a,e+"/"+S);});}});}else{q.sap.each(n,function(N,o){if(q.isArray(o)){q.each(o,function(S,e){t._saveSubContext(e,b,a,N+"/"+S);});}else if(o&&typeof o=="object"){t._saveSubContext(o,b,a,N);}});}}return b.slice(s,s+l);};J.prototype._saveSubContext=function(n,c,s,N){if(typeof n=="object"){var o=this.oModel.getContext(s+N);if(this.aFilters&&!this.bIsFiltering){if(q.inArray(o,this.filterInfo.aFilteredContexts)!=-1){c.push(o);}}else{c.push(o);}}};return J;},true);
