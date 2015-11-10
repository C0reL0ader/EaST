/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(function(){"use strict";if(String.prototype.normalize!=undefined||sap.ui.Device.browser.mobile==true){return;}else{jQuery.sap.require("sap.ui.thirdparty.unorm");jQuery.sap.require("sap.ui.thirdparty.unormdata");String.prototype.normalize=function(s){switch(s){case'NFC':return UNorm.nfc(this);case'NFD':return UNorm.nfd(this);case'NFKC':return UNorm.nfkc(this);case'NFKD':return UNorm.nfkd(this);default:return UNorm.nfc(this);}};}return;},false);
