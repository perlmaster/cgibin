//
// Function  : check_all_fields
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
// Example   : <script src="check_all_fields.js" type="text/javascript"></script>
//             onclick="return check_all_fields(document.myform1);"
//
// Notes     : Each input field must have a value specifiedd for its
//             title attribute.
//

function check_all_fields(the_form)
{
  var themessage2;
  var okflag = "good";
  var sep = " ";
  var sep2 = "";
  var num_fields = the_form.length;

  themessage2 = "You are required to enter data for the following fields:\n";
  for ( var i = 0 , length = num_fields ; i < length ; ++i) {
    if ( the_form.elements[i].value == "" ) {
      themessage2 = themessage2 + "\n" + the_form.elements[i].title;
      sep = " - ";
      okflag = "bad";
    } // IF
  } // FOR
  // alert if fields are empty and cancel form submit
  if ( okflag == "good" ) {
    the_form.submit();
  } // IF
  else {
	alert(themessage2);

    return false;
  } // ELSE
} // end of check_all_fields
