//
// Function  : copy_string_to_clipboard
//
// Purpose   : Copy data to the clipboard
//
// Inputs    : string_of_data - string to be copied to clipboard
//
// Output    : appropriate alerts
//
// Returns   : (nothing)
//
// Example   : <button onclick="copy_string_to_clipboard('string of data')">COPY</button>
//
// Notes     : (none)
//

function copy_string_to_clipboard(string_of_data)
{
	window.clipboardData.setData("Text", string_of_data);
} // end of copy_string_to_clipboard
