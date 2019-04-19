//
// Function  : check_required_fields
//
// Purpose   : Verify that all the input fields in the specified form
//             contain a value.
//
// Inputs    : the_form - the input form
//
// Output    : An alert box is displayed if any input field is empty
//
// Returns   : IF a field is missing THEN false
//
// Example   : onclick="return check_required_fields();"
//
// Notes     : Each required input field must have a value specifiedd for its
//             title attribute. The list of required fields is in a global array.
//

function check_required_fields(the_form)
{
  var themessage2;
  var okflag = "good";
  var sep = " ";
  var sep2 = "";
  var i_req;
  var req_name;

  // alert("Check for presence of the " + num_required + " required fields");

  themessage2 = "You are required to enter data for the following fields:\n";
  for ( i_req = 0 ; i_req < num_required ; ++i_req ) {
	  req_name = required_fields[i_req];
	  // alert("Check for " + req_name);
	if ( document.getElementById(req_name).value == "" ) {
      themessage2 = themessage2 + "\n" + document.getElementById(req_name).title;
      sep = " - ";
      okflag = "bad";
    } // IF
  } // FOR

  // alert if fields are empty and cancel form submit
  if ( okflag == "good" ) {
    the_form.submit();
  } // IF
  else {
	alert(themessage2 + "\n\n\n");

    return false;
  } // ELSE
} // end of check_required_fields
