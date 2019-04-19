//
// Function  : copy_cell_to_clipboard
//
// Purpose   : Copy table cell data to the clipboard
//
// Inputs    : field_id - field id of table cell tobe copied
//             background_color - new background color for copied table cell
//
// Output    : background color changed as specified
//
// Returns   : (nothing)
//
// Example   : <button onclick="copy_cell_to_clipboard('field_id','gold')">COPY</button>
//
// Notes     : (none)
//

function copy_cell_to_clipboard(field_id,background_color)
{
	var cell_data = document.getElementById(field_id).innerHTML;
	window.clipboardData.setData("Text", cell_data);
	if ( prev_copy_cell_id != 'x' ) {
		document.getElementById(prev_copy_cell_id).style.background = '#EDEDED';
	}
	document.getElementById(field_id).style.background = background_color;
	prev_copy_cell_id = field_id;

	return;
} // end of copy_cell_to_clipboard
