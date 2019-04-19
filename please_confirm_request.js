//
// File      : please_confirm_request.js
//
// Author    : Barry Kimelman
//
// Created   : February 11, 2014
//
// Purpose   : GENIE javascript support routines
//

//
// Function  : please_confirm_request
//
// Purpose   : Prompt user for confirmation of route traffic request
//
// Inputs    : the_form - form to be submitted if "yes" reply
//             operation - operation requested by the user
//             title - string identifying object to be manipulated
//
// Output    : verification prompt
//
// Returns   : If user replies "false" then return false
//
// Example   : onclick="return please_confirm_request(document.form1,'delete','my list');"
//
// Notes     : (none)
//

function please_confirm_request(the_form,operation,title)
{
	var reply;

	user_reply = confirm("Perform the requested " + operation + " operation" + " on " + title);
	if ( user_reply == true ) {
		the_form.submit();
	}
	else {
		return false;
	}
}
