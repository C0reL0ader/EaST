/*!
 * SAP UI development toolkit for HTML5 (SAPUI5/OpenUI5)
 * (c) Copyright 2009-2015 SAP SE or an SAP affiliate company.
 * Licensed under the Apache License, Version 2.0 - see LICENSE.txt.
 */

// Provides enumeration sap.ui.model.OperationMode
sap.ui.define(['jquery.sap.global'],
	function(jQuery) {
	"use strict";


	/**
	* @class
	* Different modes for executing service operations (filtering, sorting)
	*
	* @static
	* @public
	* @alias sap.ui.model.odata.OperationMode
	*/
	var OperationMode = {
			/**
			 * Operations are executed on the Odata service, by appending corresponding URL parameters ($filter, $orderby).
			 * Each change in filtering or sorting is triggering a new request to the server.
			 * @public
			 */
			Server: "Server",
	
			/**
			 * Operations are executed on the client, all entries must be avilable to be able to do so.
			 * The initial request fetches the complete collection, filtering and sorting does not trigger further requests
			 * @public
			 */
			Client: "Client"
	};

	return OperationMode;

}, /* bExport= */ true);
