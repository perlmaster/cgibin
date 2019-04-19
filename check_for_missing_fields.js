//
// Function  : check_for_missing_fields
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
// Example   : <input title="submit button" type="submit" value="Submit This Stuff"
//                     onclick="return validate_form(document.form1)"
//
// Notes     : Each input field must have a value specifiedd for its
//             title attribute.
//

function validate_form(the_form)
{
	// var inputs = the_form.getElementsByTagName("input");
	var inputs = the_form.elements;

	var flag = true;
	var len = inputs.length;
	var i;
	var input;
	var field_type;
	var field_name;
	var field_title;
	var the_message = "You are required to enter/select/check data for the following fields :\n";
	var index;
	var num_missing_select = 0;

	var radio_hashlist = new Array();
	var num_uncheked_radio_buttons = 0;
	var num_radios = 0;

	var cbox_hashlist = new Array();
	var num_unchecked_cbox = 0;
	var num_cbox = 0;

	for ( i = 0 ; i < len ; ++i ) {
		input = inputs[i];
		field_type = input.type.toLowerCase();
		field_name = input.name;
		field_title = input.title;
		if ( field_type == "submit" ) {
			continue;
		}

		if ( field_type == "select-one" || field_type == "select-multiple" ) {
			// alert("Found a missing select");
			index = input.selectedIndex;
			if ( index <= 0 ) {
				num_missing_select += 1;
				// alert("Nothing selected for list " + field_title);
				the_message += "\n" + field_title;
			}
			continue;
		}

		if ( field_type == "radio" ) {
			num_radios += 1;
			if ( ! (field_name in radio_hashlist) ) {
				radio_hashlist[field_name] = 0;
			}
			if ( input.checked == true ) {
				radio_hashlist[field_name] = 1;
			}
			continue;
		}

		if ( field_type == "checkbox" ) {
			num_cbox += 1;
			if ( ! (field_name in cbox_hashlist) ) {
				cbox_hashlist[field_name] = 0;
			}
			if ( input.checked == true ) {
				cbox_hashlist[field_name] = 1;
			}
			continue;
		}

		if ( input.value == "" ) {
			flag = false;
			// alert("No value was specified for field " + field_title + " which is a " + field_type);
			the_message += "\n" + field_title;
		}
	} // FOR loop over all ihnput fields

	if ( num_radios > 0 ) {
		for ( var hashkey in radio_hashlist ) {
			if ( radio_hashlist[hashkey] == 0 ) {
				// alert("Nothing checked for radio button group '" + hashkey + "'");
				the_message += "\n" + hashkey;
				num_uncheked_radio_buttons += 1;
			}
		}
	}

	if ( num_cbox > 0 ) {
		for ( var hashkey in cbox_hashlist ) {
			if ( cbox_hashlist[hashkey] == 0 ) {
				// alert("Nothing checked for checkbox button group '" + hashkey + "'");
				the_message += "\n" + hashkey;
				num_unchecked_cbox += 1;
			}
		}
	}

	if ( flag && num_uncheked_radio_buttons == 0 && num_unchecked_cbox == 0 && num_missing_select == 0 ) {
		alert("All fields are ok");
	}
	else {
		alert(the_message);
	}
	return flag;
}
