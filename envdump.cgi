#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : envdump.cgi
#
# Author    : Barry Kimelman
#
# Created   : February 27, 2014
#
# Purpose   : CGI script to dump environment variables.
#
######################################################################

use strict;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use Time::Local;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

require "utilities.pl";
require "CGI-DUMP-COOKIES.pl";
require "CGI-DUMP-ENV.pl";

my ( $cgi , $footer_html , $header_html , $script_name );
my $title = "Environment Variables and Cookies";

######################################################################
#
# Function  : MAIN
#
# Purpose   : CGI script to display a multiple month calendar.
#
# Inputs    : parameters passed in by web server
#
# Output    : appropriate data
#
# Returns   : nothing
#
# Example   : https://10.251.1.11/genconfig/mycal.cgi
#
# Notes     : (none)
#
######################################################################

my ( @list , $status , $errmsg , $buffer , $style , $errors , $errmsg2 );

$script_name = $ENV{"SCRIPT_NAME"};
@list = split(/\//,$script_name);
$script_name = $list[$#list];

$cgi = new CGI;

print $cgi->header;

print $cgi->start_html(
			-title => "ENV Dump" ,
			-style=>[
				{-src=>'/styles.css'},
				{-src=>'/fieldset.css'}
			],
		);
print $cgi->h1("ENV Dump");

cgi_dump_cookies($cgi,"Cookies Listing");
cgi_dump_env_variables("CGI script environment variables $script_name");

print $cgi->end_html;

exit 0;
