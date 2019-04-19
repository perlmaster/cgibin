//
// Function  : hide_divider , show_divider , toggle_dividers
//
// Purpose   : Hide or show a divider
//
// Inputs    : the_form - the input form
//
// Output    : appropriate alerts
//
// Returns   : (nothing)
//
// Example   : <script src="hide_show_divider.js" type="text/javascript"></script>
//
// Notes     : (none)
//

function hide_divider(divider_id) {
var div_obj = document.getElementById(divider_id);
div_obj.style.display = 'none'; 
}

function show_divider(divider_id) {
var div_obj = document.getElementById(divider_id);
div_obj.style.display = 'block';
}

function toggle_dividers(first_divider,second_divider) {
var div_obj;

div_obj = document.getElementById(first_divider);
div_obj.style.display = 'none';

div_obj = document.getElementById(second_divider);
div_obj.style.display = 'block';
}

function goto_page(current_page,last_page) {
	var page_number;
	var page_number_field;
	var new_page;
	var reInteger = /^\\d+\$/;

	page_number_field = "page_number_" + current_page;
	page_number = document.getElementById(page_number_field);
	if ( page_number.value == "" ) {
		alert("You forgot the page number !");
	}
	else {
		if ( reInteger.test(page_number.value) ) {
			if ( page_number.value > last_page ) {
				alert(page_number.value + " is beyond the last page which is " + last_page);
			}
			else {
				new_page = "divider_" + page_number.value;
				toggle_dividers(current_page,new_page);
			}
		}
		else {
			alert("Non numeric data detected in '" + page_number.value + "'");
		}
	}
}
