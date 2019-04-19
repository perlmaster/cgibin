#!/opt/gns/perl/bin/perl

######################################################################
#
# File      : CGI-DUMP-PARAMETERS.pl
#
# Author    : Barry Kimelman
#
# Created   : March 10, 2011
#
# Purpose   : Display CGI script parameters.
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
# Function  : cgi_dump_script_parameters
#
# Purpose   : Display the values of the parameters passed by the web server
#             to a CGI script.
#
# Inputs    : $_[0] - CGI session object
#             $_[1] - optional title
#
# Output    : CGI script parameters
#
# Returns   : (nothing)
#
# Example   : cgi_dump_script_parameters($cgi,"CGI script parameters for foo.cgi");
#
# Notes     : (none)
#
######################################################################

sub cgi_dump_script_parameters
{
	my ( $cgi , $title ) = @_;
	my ( $cgi_parms_buffer , @cgi_parms_list , $value , @list , $index , $count );

	print qq~
<div style="padding-left: 20px;">
~;
	unless ( defined $title ) {
		$title = "CGI script parameters :<BR>\n";
	} # UNLESS

	@cgi_parms_list = $cgi->param();
	print "<BR><H4>$title</H4>\n";
	if ( 1 > @cgi_parms_list ) {
		print "<H4>No CGI script parameters are defined</H4><BR>\n";
	} # IF
	else {
		print qq~
<TABLE border="1" bordercolor="black" cellspacing="0" cellpadding="3">
<THEAD style="background-color: lightskyblue;">
<TR><TH>Parameter</TH><TH>Value</TH></TR>
</THEAD>
<TBODY style="font-weight: bold; font-family: Courier New, Courier; background-color: lightgrey;">
~;
		foreach my $cgi_param ( sort {lc $a cmp lc $b } @cgi_parms_list ) {
			@list = $cgi->param($cgi_param);
			$count = scalar @list;
			if ( $count < 1 ) {
				$value = "\&nbsp;";
			} # IF
			else {
				for ( $index = 0 ; $index <= $#list ; ++$index ) {
					unless ( defined $list[$index] && 0 < length $list[$index] ) {
						$list[$index] = '&nbsp;';
					} # UNLESS
					else {
						$list[$index] =~ s/\r\n/<BR>/g;
						$list[$index] =~ s/ /\&nbsp;/g;
					}  # ELSE
				} # FOR
				if ( $count > 1 ) {
					$value = join("<BR>",map { "[$_] :<BR>$list[$_]" } ( 0 .. $#list ));
				} # IF
				else {
					$value = join(" , ",@list);
				} # ELSE
			} # ELSE
			print "<TR><TD VALIGN='top'><B>$cgi_param</B></TD><TD>${value}</TD></TR>\n";
		} # FOREACH
		print "</TBODY></TABLE><BR>\n";
	} # ELSE
	print "</div>\n";

	return;
} # end of cgi_dump_script_parameters

######################################################################
#
# Function  : cgi_dump_script_parameters_double
#
# Purpose   : Display the values of the parameters passed by the web server
#             to a CGI script (2 per row).
#
# Inputs    : $_[0] - CGI session object
#             $_[1] - optional title
#
# Output    : CGI script parameters
#
# Returns   : (nothing)
#
# Example   : cgi_dump_script_parameters_double($cgi,"CGI script parameters for foo.cgi");
#
# Notes     : (none)
#
######################################################################

sub cgi_dump_script_parameters_double
{
	my ( $cgi , $title ) = @_;
	my ( $cgi_parms_buffer , @cgi_parms_list , $value , @list , $index , $count );
	my ( @sorted , $cgi_param , $num_parms , $index2 );

	print qq~
<div style="padding-left: 20px;">
~;
	unless ( defined $title ) {
		$title = "CGI script parameters :<BR>\n";
	} # UNLESS

	@cgi_parms_list = $cgi->param();
	print "<BR><H4>$title</H4>\n";
	if ( 1 > @cgi_parms_list ) {
		print "<H4>No CGI script parameters are defined</H4><BR>\n";
	} # IF
	else {
		print qq~
<TABLE border="1" bordercolor="black" cellspacing="0" cellpadding="3">
<THEAD style="background-color: lightskyblue;">
<TR>
<TH>Parameter</TH><TH>Value</TH><TH>Parameter</TH><TH>Value</TH>
</TR>
</THEAD>
<TBODY style="font-weight: bold; font-family: Courier New, Courier; background-color: lightgrey;">
~;
		@sorted = sort {lc $a cmp lc $b } @cgi_parms_list;
		$num_parms = scalar @sorted;
		for ( $index2 = 0 ; $index2 <= $#sorted ; ++$index2 ) {
			unless ( $index2 & 1 ) {
				print "<TR>\n";
			} # UNLESS
			$cgi_param = $sorted[$index2];
			@list = $cgi->param($cgi_param);
			$count = scalar @list;
			if ( $count < 1 ) {
				$value = "\&nbsp;";
			} # IF
			else {
				for ( $index = 0 ; $index <= $#list ; ++$index ) {
					unless ( defined $list[$index] && 0 < length $list[$index] ) {
						$list[$index] = '&nbsp;';
					} # UNLESS
					else {
						$list[$index] =~ s/\r\n/<BR>/g;
						$list[$index] =~ s/ /\&nbsp;/g;
					}  # ELSE
				} # FOR
				if ( $count > 1 ) {
					$value = join("<BR>",map { "[$_] :<BR>$list[$_]" } ( 0 .. $#list ));
				} # IF
				else {
					$value = join(" , ",@list);
				} # ELSE
			} # ELSE
			print "<TD><B>$cgi_param</B></TD><TD>${value}</TD>\n";
			if ( $index2 & 1 ) {
				print "</TR>\n";
			} # IF
		} # FOR
		if ( $num_parms & 1 ) {
			print "<TD>\&nbsp;</TD><TD>\&nbsp;</TD></TR>\n";
		} # IF
		print "</TBODY></TABLE><BR>\n";
	} # ELSE
	print "</div>\n";

	return;
} # end of cgi_dump_script_parameters_double

1;
