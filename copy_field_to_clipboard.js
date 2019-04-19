//
// Function  : copy_field_to_clipboard
//
// Purpose   : Copy a field's data to the clipboard
//
// Inputs    : field_id - id of field containing value to be copied to the clipboard
//
// Output    : (none)
//
// Returns   : (nothing)
//
// Example   : <button onclick="copy_field_to_clipboard('field_id')">COPY FIELD</button>
//
// Notes     : (none)
//

function copy_field_to_clipboard(field_id)
{
	var input = document.getElementById(field_id);
	window.clipboardData.setData("Text", input.value);
} // end of copy_field_to_clipboard
