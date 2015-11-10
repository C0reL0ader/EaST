/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */
sap.ui.define(['jquery.sap.global','sap/ui/core/message/MessageProcessor'],function(q,M){"use strict";var C=M.extend("sap.ui.core.message.ControlMessageProcessor",{constructor:function(){M.apply(this,arguments);},metadata:{}});C.prototype.setMessages=function(m){this.mOldMessages=q.isEmptyObject(this.mMessages)?m:this.mMessages;this.mMessages=m||{};this.checkMessages();delete this.mOldMessages;};C.prototype.checkMessages=function(){var m,t=this;q.each(this.mOldMessages,function(T,o){var b;var p=T.split('/');var c=sap.ui.getCore().byId(p[0]);if(!c){return;}b=c.getBinding(p[1]);m=t.mMessages[T]?t.mMessages[T]:[];if(b){b._fireMessageChange({messageSource:'control',messages:m});}else{c.updateMessages(p[1],m);}});};return C;},true);
