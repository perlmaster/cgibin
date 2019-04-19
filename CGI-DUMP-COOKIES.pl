#!/opt/gns/perl/bin/perl

######################################################################
#
# File      : CGI-DUMP-COOKIES.pl
#
# Author    : Barry Kimelman
#
# Created   : March 10, 2011
#
# Purpose   : Display of cookies.
#
######################################################################

use strict;
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use CGI::Cookie;
use URI::Escape;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

######################################################################
#
# Function  : cgi_dump_cookies
#
# Purpose   : Display the values of the browser cookies.
#
# Inputs    : $_[0] - CGI session object
#             $_[1] - optional title
#
# Output    : Browser cookies.
#
# Returns   : (nothing)
#
# Example   : cgi_dump_cookies($cgi,"Cookies Listing");
#
# Notes     : (none)
#
######################################################################

sub cgi_dump_cookies
{
	my ( $cgi , $title ) = @_;
	my ( $status , %cookie_hash , @cookie_data , $ref_cookie , %hash , $data , $cookie_data , $spaces );

	unless ( defined $title ) {
		$title = "Cookies";
	} # UNLESS

	print qq~
<H3>${title}</H3>
<TABLE border="1" bordercolor="black" cellspacing="0" cellpadding="3">
<THEAD style="background-color: lightskyblue;">
<TR><TH>Cookie Name</TH><TH>Cookie Value</TH></TR>
</THEAD>
<TBODY style="font-weight: bold; font-family: Courier New, Courier; background-color: lightgrey;">
~;

	%cookie_hash = CGI::Cookie->fetch;
	$status = 1;
	foreach my $cookie_name ( keys %cookie_hash ) {
		$status = 0;
		$ref_cookie = $cookie_hash{$cookie_name}->{'value'};
		@cookie_data = @$ref_cookie;
		if ( 1 == scalar @cookie_data ) {
			$cookie_data = $cookie_data[0];
			unless ( defined $cookie_data && $cookie_data =~ m/\S/ ) {
				$cookie_data = '&nbsp;';
			} # UNLESS
			print "<tr><td>$cookie_name</td><td>$cookie_data</td></tr>\n";
		} # IF
		else {
			%hash = @cookie_data;
			print "<tr><td>${cookie_name}</td>\n<td>";
			print "<TABLE border='0' cellspacing='0' cellpadding='3'>\n";

			$spaces = '&nbsp;' x 2;
			foreach my $key ( sort { lc $a cmp lc $b } keys %hash ) {
				$data = $hash{$key};
				unless ( defined $data && 0 < length $data ) {
					$data = "(empty)";
				} # UNLESS
				print "<TR><TD>$key</TD><TD>${spaces}=>${spaces}</TD><TD>$data</TR></TR>\n";
			} # FOREACH
			print "</TABLE>\n";

			print "</td></tr>\n";
		} # ELSE
	} # FOREACH
	print "</table>\n";
	if ( $status ) {
		print "<H3>**  No Cookies  **</H3>\n";
	} # IF
	print "<BR>\n";

	return;
} # end of cgi_dump_cookies

1;
