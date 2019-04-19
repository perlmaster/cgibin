#!/opt/gns/perl/bin/perl

######################################################################
#
# File      : CGI-DUMP-ENV.pl
#
# Author    : Barry Kimelman
#
# Created   : March 10, 2011
#
# Purpose   : Display CGI script environment variables.
#
######################################################################

use strict;
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use URI::Escape;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

######################################################################
#
# Function  : cgi_dump_env_variables
#
# Purpose   : Display the values of the parameters passed by the web server
#             to a CGI script.
#
# Inputs    : $_[0] - optional title
#
# Output    : CGI script parameters
#
# Returns   : (nothing)
#
# Example   : cgi_dump_env_variables("CGI script environment variables foo.cgi");
#
# Notes     : (none)
#
######################################################################

sub cgi_dump_env_variables
{
	my ( $title ) = @_;
	my $value;

	unless ( defined $title ) {
		$title = "<BR>Environment variables<BR>";
	} # UNLESS

	print "<H4>$title</H4>\n";

	print qq~
<TABLE border="2" bordercolor="black" cellspacing="0" cellpadding="3">
<THEAD style="background-color: lightskyblue;">
<TR><TH>Name</TH><TH>Value</TH></TR>
</THEAD>
<TBODY style="font-weight: bold; font-family: Courier New, Courier; background-color: lightgrey;">
~;

	foreach my $env ( sort keys %ENV ) {
		$value = $ENV{$env};
		unless ( defined $value && 0 < length $value ) {
			$value = '&nbsp;';
		} # UNLESS
		else {
			$value =~ s/\&/\&amp;/g;
		} # ELSE
		print "<tr><td>$env</td><td>$value</td></tr>\n";
	} # FOREACH
	print "</tbody>\n</table><BR>\n";

	return;
} # end of cgi_dump_env_variables

1;
