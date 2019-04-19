//
// Function  : clearForm
//
// Purpose   : Clear all the fields in a form.
//
// Inputs    : the_form - the input form
//
// Output    : (none)
//
// Returns   : (nothing)
//
// Example   : onclick="return clearForm(document.myform1);"
//
// Notes     : (none)
//

function clearForm(oForm)
{
	var elements = oForm.elements;
	var count = elements.length;
	var index;
	var field_type;
	var name;

	var user_reply = confirm("Are you sure you want to clear all the data fields ?");
	if ( user_reply == true ) {
		for ( index = 0 ; index < count ; index++ )
		{
			name = elements[index].tagName;
			if ( name == 'FIELDSET' ) {
				continue;
			}

			field_type = elements[index].type.toLowerCase();
			switch(field_type)
			{
				case "text":
				case "password":
				case "textarea":
				case "hidden":	
					elements[index].value = "";
					break;

				case "radio":
				case "checkbox":
					if ( elements[index].checked ) {
						elements[index].checked = false;
					}
					break;

				case "select-one":
				case "select-multiple":
					elements[index].selectedIndex = -1;
					break;

				default:
					break;
			} // SWITCH
		} // FOR
	}
}
