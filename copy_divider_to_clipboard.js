//
// Function  : copy_divider_to_clipboard
//
// Purpose   : Copy data to the clipboard
//
// Inputs    : divider_id - id of field containing value to be copied to the clipboard
//
// Output    : appropriate alerts
//
// Returns   : (nothing)
//
// Example   : <button onclick="copy_divider_to_clipboard('divider_id')">COPY</button>
//
// Notes     : (none)
//

function copy_divider_to_clipboard(divider_id)
{
	var div_data = document.getElementById(divider_id).innerHTML;
	var buffer = div_data.replace(/<BR>/gm,'\r\n');
	window.clipboardData.setData("Text", buffer);
} // end of copy_divider_to_clipboard
