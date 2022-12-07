#!/usr/bin/perl -w

######################################################################
#
# File      : template.cgi
#
# Author    : Barry Kimelman
#
# Created   : September 1, 2020
#
# Purpose   : A template for CGI scripts
#
######################################################################

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use File::Spec;
use File::Basename;
use DBI;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;
use database;

require "CGI-DUMP-COOKIES.pl";
require "CGI-DUMP-ENV.pl";
require "CGI-DUMP-PARAMETERS.pl";

my $cgi;
my $script_name = "";
my %parameters = ();
my $top_level_href;
my $title = "CGI Template Title";

my $onmouseover =<<MOUSE;
onMouseOver="this.style.background='peru';this.style.color='white';this.style.fontWeight=900;return true;"
onMouseOut="this.style.backgroundColor=''; this.style.color='black';this.style.fontWeight=500;"
MOUSE

######################################################################
#
# Function  : display_error
#
# Purpose   : Display an error message.
#
# Inputs    : @_ - array of strings comprising error message
#
# Output    : requested error message
#
# Returns   : (nothing)
#
# Example   : display_error("Hello from here ",$xx);
#
# Notes     : (none)
#
######################################################################

sub display_error
{
	my ( $message );

	$message = join("",@_);
	print "<span class='redtext'>${message}</span>\n";

	return;
} # end of display_error

######################################################################
#
# Function  : MAIN
#
# Purpose   : Entry point for this program.
#
# Inputs    : @ARGV - array of parameters
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : (none)
#
# Notes     : (none)
#
######################################################################

my ( $style );
my ( $buffer , $status , $errmsg , $errors , $errmsg2 );

$cgi = new CGI;
%parameters = map { $_ , $cgi->param($_) } $cgi->param();

print $cgi->header;

print $cgi->start_html(
			-title => "$title" ,
			-style=>[
				{-src=>'/tooltip.css'},
				{-src=>'/styles.css'},
				{-src=>'/fieldset.css'},
				{-src=>'/print.css'}
			],
			-script=>[
				{-type=>'javascript', -src=>'/check_all_fields.js'},
				{-type=>'javascript', -src=>'/check_for_missing_fields.js'},
				{-type=>'javascript', -src=>'/clearForm.js'},
				{-type=>'javascript', -src=>'/copy_cell_to_clipboard.js'},
				{-type=>'javascript', -src=>'/copy_field_to_clipboard.js'},
				{-type=>'javascript', -src=>'/copy_divider_to_clipboard.js'},
				{-type=>'javascript', -src=>'/copy_string_to_clipboard.js'},
				{-type=>'javascript', -src=>'/hide_show_divider.js'}
			]
		);

print $cgi->h1("$title");

$script_name = basename($0);
$top_level_href = "<A class='boldlink2' HREF='${script_name}'>Return to Main Screen</A>";
print "<H3>Welcome from $script_name</H3>\n";

print qq~
<script type="text/javascript">
function general_submission(form_name)
{
	document.getElementById('notes').value = "just a general submission";
	document.getElementById('job_description').value = "just a general submission";
}
</script>
~;

cgi_dump_script_parameters($cgi,"CGI script parameters");

cgi_dump_env_variables("CGI script environment variables");

print $cgi->end_html;

exit 0;
