//
// Function  : show_confirm
//
// Purpose   : Prompt the user for verification after they have clicked a submit button.
//
// Inputs    : the_form - the input form
//
// Output    : Confirmartion prompt
//
// Returns   : IF confirmation denied THEN false
//
// Example   : <script src="sgow_confirm.js" type="text/javascript"></script>
//             onclick="return show_confirm(document.myform1);"
//
// Notes     : (none)
//

function show_confirm(the_form)
{
var user_reply = confirm("Are you sure you want to do this ?");
if ( user_reply == true ) {
  the_form.submit();
}
else {
  return false;
}
} // end of show_confirm
