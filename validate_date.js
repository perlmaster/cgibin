//
// Function  : validate_date
//
// Purpose   : Validater a date in YYYY-MM-DD format
//
// Inputs    : datefield - date field object
//             msgtext - text to be included in error messages
//
// Output    : An alert box is displayed if an error is detected
//
// Returns   : IF a field is missing THEN false ELSE true
//
// Example   : onblur="validate_date(document.myform1.datefield,'my date field');"
//
// Notes     : (none)
//

function validate_date(datefield,msgtext)
{
	var dateString = datefield.value;

	// First check for the pattern : YYYY-MM-DD

	if ( !/^\d{4}-\d{1,2}-\d{1,2}$/.test(dateString) ) {
		alert("Invalid date format for " + msgtext + " : bad characters");
		return false;
	}

	// Parse the date parts to integers

	var parts = dateString.split("-");
	var day = parseInt(parts[2], 10);
	var month = parseInt(parts[1], 10);
	var year = parseInt(parts[0], 10);

	// Check the ranges of month and year
	if ( year < 1000 || year > 3000 || month == 0 || month > 12 ) {
		alert("Invalid date format for " + msgtext + " : year or month out of range");
		return false;
	}

	var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

	// Adjust for leap years
	if ( year % 400 == 0 || (year % 100 != 0 && year % 4 == 0) )
		monthLength[1] = 29;

	// Check the range of the day
	if ( day > 0 && day <= monthLength[month - 1] ) {
		return true;
	}
	else {
		alert("Invalid date format for " + msgtext + " : day of month is out of range");
		return false;
	}
} // end of validate_date
