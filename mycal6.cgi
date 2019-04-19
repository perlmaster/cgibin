#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : mycal.cgi
#
# Author    : Barry Kimelman
#
# Created   : July 19, 2012
#
# Purpose   : CGI script to display a multiple month calendar.
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

my ( $cgi , $footer_html , $header_html , $script_name , $top_level_href );
my ( $current_year , $current_month , $current_mday );
my $screen_title = "Multiple Month Calendar";

my @months = ( "Jan" , "Feb" , "Mar" , "Apr" , "May" , "Jun" , "Jul" , "Aug" ,
				"Sep" , "Oct" , "Nov" , "Dec" );
my @full_months = ( "January" , "February" , "March" , "April" , "May" , "June" ,
						"July" , "August" , "September" , "October" , "November" ,
						"December" );
my @weekdays = ( "Sunday" , "Monday" , "Tuesday" , "Wednesday" , "Thursday" ,
					"Friday" , "Saturday" );
my @month_days = ( 31 , 28 , 31 , 30 , 31 , 30 , 31 , 31 , 30 , 31 , 30 , 31 );

######################################################################
#
# Function  : is_leap_year
#
# Purpose   : Check for a leap year
#
# Inputs    : $_[0] - year to be tested
#
# Output    : (none)
#
# Returns   : IF leap year THEN 1 ELSE 0
#
# Example   : $leap = is_leap_year(1999);
#
# Notes     : (none)
#
######################################################################

sub is_leap_year
{
	my ( $year ) = @_;
	my ( $leap );

	if ( (($year%4 == 0) && ($year%100 != 0)) || ($year%400 == 0) ) {
		$leap = 1;
	} # IF
	else {
		$leap = 0;
	} # ELSE

	return $leap;
} # end of is_leap_year

######################################################################
#
# Function  : generate_calendar
#
# Purpose   : Generate the HTML code for a calendar month.
#
# Inputs    : $_[0] - month number
#             $_[1] - year number
#
# Output    : (none)
#
# Returns   : HTML code representing calendar
#
# Example   : $calendar = generate_calendar(8,2012);  # August 2012
#
# Notes     : (none)
#
######################################################################

sub generate_calendar
{
	my ( $month_num , $year_num ) = @_;
	my ( $startDate , $string , @week_dates , $day_of_month , $wday_index , $index1 );
	my ( $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst , $max_date );
	my ( @headers , $current_month_flag , $cal_html , $month_name , $title );

	$current_month_flag = ( $month_num == $current_month && $year_num == $current_year ) ? 1 : 0;
	$month_num -= 1;
	$month_name = $full_months[$month_num];

	$cal_html =<<CAL1;
<BR>
<TABLE border="1" cellspacing="0" cellpadding="3" width="400px">
<THEAD>
<TR class="th3"><TH colspan="7">$month_name $year_num</TH></TR>
</THEAD>
<TBODY class="bluetext3">
CAL1

	$startDate = timelocal(0, 0, 0, 1, $month_num, $year_num);  # 08/28/2009 at 11:00 PM
	$string = localtime($startDate);
	( $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst ) =
				localtime($startDate);

	if ( is_leap_year($year_num) ) {
		$month_days[1] = 29;
	} # IF

	@week_dates = map { -1 } ( 0 .. 6 );
	$day_of_month = 1;
	for ( $wday_index = $wday ; $wday_index <= 6 ; ++$wday_index ) {
		$week_dates[$wday_index] = $day_of_month;
		$day_of_month += 1;
	} # FOR

	@headers = map { substr($_,0,3) } @weekdays;
	$cal_html .= "<TR>".join("",map { "<TD>$_</TD>" } @headers)."</TR>\n";

	$index1 = $wday;
	while ( 1 ) {
		$max_date = (sort { $b <=> $a } @week_dates)[0];
		$cal_html .= "<TR>\n";
		for ( $wday_index = 0 ; $wday_index <= 6 ; ++$wday_index ) {
			if ( $week_dates[$wday_index] < 1 ) {
				$cal_html .= "<TD>\&nbsp;</TD>";
			} # IF
			else {
				$title = "$weekdays[$wday_index] ${month_name} $week_dates[$wday_index], ${year_num}";
				if ( $current_month_flag && $week_dates[$wday_index] == $current_mday ) {
					$cal_html .= "<TD title='$title' class='redtext5_silverback'>$week_dates[$wday_index]</TD>";
				} # IF
				else {
					$cal_html .=<<CAL2;
<TD title='$title' onclick="add_note(this);">$week_dates[$wday_index]</TD>
CAL2
				} # ELSE
			} # ELSE
		} # FOR
		$cal_html .= "</TR>\n";
		if ( $max_date >= $month_days[$month_num] ) {
			last;
		} # IF
		@week_dates = map { -1 } ( 0 .. 6 );
		for ( $wday_index = 0 ; $wday_index <= 6 ; ++$wday_index ) {
			$max_date += 1;
			$week_dates[$wday_index] = $max_date;
			if ( $max_date >= $month_days[$month_num] ) {
				last;
			} # IF
		} # FOR
	} # WHILE
	$cal_html .= "</TBODY></TABLE>\n";

	return $cal_html;
} # end of generate_calendar

######################################################################
#
# Function  : generate_main_screen
#
# Purpose   : Generate main screen
#
# Inputs    : (none)
#
# Output    : HTML for main screen
#
# Returns   : nothing
#
# Example   : generate_main_screen($year,$mon);
#
# Notes     : (none)
#
######################################################################

sub generate_main_screen
{
	my ( $year , $mon ) = @_;

#--------------------------------------#
# Generate a prompt and the <FORM> tag #
#--------------------------------------#
	print qq~
<BR>
<FORM id="siteform" name="siteform" method="POST" action="$script_name">
  <fieldset class="edit_background" style="width: 450px;">
  <legend class="edit_legend">Enter month and year</legend>

<BR>
  <label for="txtSitename">Month\&nbsp;\&nbsp;</label>
  <input class="input_fieldset1" title="Month" type="text" name="month" id="month" size="10"
  value="${mon}" />
  <br /> <br />

  <label for="txtSitename">Year\&nbsp;\&nbsp;</label>
  <input class="input_fieldset1" title="Year" type="text" name="year" id="year" size="10"
  value="${year}" />
  <br /> <br />

  <label for="txtSitename"># Months\&nbsp;\&nbsp;</label>
  <input class="input_fieldset1" title="Number of Months" type="text" name="num_months" id="num_months" size="10"
  value="2" />
  <br /> <br />

  </fieldset>
~;

#------------------------------------------------------------#
# Generate the end of the form, including the submit buttons #
#------------------------------------------------------------#
	print qq~
<BR>
<input class="darktext2" type="submit" name="submit1" value="Display Calendar"
onclick="return check_all_fields(document.siteform,'$script_name');"
onMouseOver="this.style.background='peru';this.style.color='white';this.style.fontWeight=900;return true;"
onMouseOut="this.style.backgroundColor=''; this.style.color='black';this.style.fontWeight=500;"
/>
</FORM>
<script type="text/javascript" language="javascript">
    document.getElementById("month").focus();
</script>

<BR>
</div>
~;

#-------------------------------------------------------------------#
# Write out the JavaScript code used to check for empty form fields #
#-------------------------------------------------------------------#
	print qq~
<script type="text/javascript" src="check_all_fields.js"></script>
~;

	return;
} # end of generate_main_screen

######################################################################
#
# Function  : read_file_contents
#
# Purpose   : Generate the add new entry screen.
#
# Inputs    : $_[0] - name of file
#             $_[1] - reference to buffer to receive data
#             $_[2] - reference to error message buffer
#
# Output    : (none)
#
# Returns   : IF error THEN negative ELSE 0
#
# Example   : $status = read_file_contents($filename,\$buffer,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub read_file_contents
{
	my ( $filename , $ref_buffer , $ref_errmsg ) = @_;
	my ( @lines );

	$$ref_errmsg = "";
	unless ( open(INPUT,"<$filename") ) {
		$$ref_errmsg = "open failed for file '$filename' : $!";
		return -1;
	} # UNLESS

	@lines = <INPUT>;
	close INPUT;
	$$ref_buffer = join("",@lines);

	return 0;
} # end of read_file_contents

######################################################################
#
# Function  : display_calendar
#
# Purpose   : Display a page containing the generated calendar.
#
# Inputs    : $_[0] - previously generated calendar
#
# Output    : calendar page
#
# Returns   : (nothing)
#
# Example   : display_calendar($cal);
#
# Notes     : (none)
#
######################################################################

sub display_calendar
{
	my ( $calendar ) = @_;

	print qq~
<TABLE border="1" bordercolor="red">
<THEAD>
</THEAD>
<TBODY>
<TR VALIGN="top"> <TD>${calendar}</TD>
<TD WIDTH="50px">\&nbsp;</TD>
<TD id="notes" name="notes"><BR></TD>
</TR>
</TBODY>
</TABLE>
~;

	return;
} # end of display_calendar

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

my ( $title , @list , $buffer , $month , $year , $num_months , $count , $style );
my ( $status , $errmsg , $errmsg2 , $errors , %cal , $mode );
my ( $sec , $min , $hour , $wday , $yday , $isdst , $clock , $cal );
my ( $bigcal );

$clock = time;
( $sec , $min , $hour , $current_mday , $current_month , $current_year , $wday , $yday , $isdst ) = localtime($clock);
$current_year += 1900;
$current_month += 1;

$title = "Monthly Calendar";

$script_name = pop @list;
$script_name = $ENV{"SCRIPT_NAME"};
@list = split(/\//,$script_name);
$script_name = $list[$#list];

$style = "";

$cgi = new CGI;

print $cgi->header;

print $cgi->start_html(
			-title => "$title" ,
			-style=>[
				{-src=>'/styles.css'},
				{-src=>'/fieldset.css'}
			],
			-script=>[
				{-type=>'javascript', -src=>'/check_all_fields.js'},
				{-type=>'javascript', -src=>'/hide_show_divider.js'}
			]
		);
print $cgi->h1("$title");

print qq~
<script type="text/javascript">
function add_note(cell)
{
	cell.style.backgroundColor='peru';
	var celldate = cell.title;
	var buffer = prompt("Enter the note : ", "the note goes here here");
	document.getElementById('notes').innerHTML += "<H3>" + celldate + "<BR>" + buffer + "</H3>";
}
</script>
~;

$top_level_href = "<A class='boldlink2' HREF=\"${script_name}\">Click here to return to top level</A>";

$mode = $cgi->param('mode');
%cal = ();
$cal{'month'} = $cgi->param("month");
$cal{'year'} = $cgi->param("year");
$cal{'num_months'} = $cgi->param("num_months");

$cal = "";
if ( defined $mode && $mode eq 'batch' ) {
	unless ( defined $cal{'month'} && 0 < length $cal{'month'} ) {
		$cal{'month'} = $current_month;
	} # UNLESS
	unless ( defined $cal{'year'} && 0 < length $cal{'year'} ) {
		$cal{'year'} = $current_year;
	} # UNLESS
	unless ( defined $cal{'num_months'} && 0 < length $cal{'num_months'} ) {
		$cal{'num_months'} = 1;
	} # UNLESS

	for ( $count = 1 ; $count <= $cal{'num_months'} ; ++$count , ++$cal{'month'} ) {
		$cal .= generate_calendar($cal{'month'},$cal{'year'});
	} # FOR

	##  display_calendar($cal);
	print "$cal\n";

	print "<BR><BR>${top_level_href}<BR><BR>\n";
} elsif ( defined $cal{'month'} && 0 < length $cal{'month'}  && defined $cal{'year'} && 0 < length $cal{'year'} &&
					defined $cal{'num_months'} && 0 < length $cal{'num_months'} ) {
	$bigcal =<<BIGTABLE1;
<TABLE border="0" cellspacing="0" cellpadding="3">
<TBODY>
BIGTABLE1
	for ( $count = 1 ; $count <= $cal{'num_months'} ; ++$count , ++$cal{'month'} ) {
		if ( $cal{'month'} > 12 ) {
			$cal{'month'} = 1;
			$cal{'year'} += 1;
		} # IF
		$cal = generate_calendar($cal{'month'},$cal{'year'});
		if ( $count & 1 ) {
			$bigcal .= "<TR valign='top'><TD>$cal</TD>\n";
		} # IF
		else {
			$bigcal .= "<TD width='40px'>\&nbsp;</TD><TD>$cal</TD></TR>\n";
		} # ELSE
	} # FOR
	##  display_calendar($cal);
	##  print "$cal\n";
	if ( $cal{'num_months'} & 1 ) {
		$bigcal .= "<TD colspan='2'>\&nbsp;</TD></TR>\n";
	} # IF
	print "$bigcal\n";
	print "<BR><BR>${top_level_href}<BR><BR>\n";
} # IF
else {
	generate_main_screen($current_year,$current_month);
} # ELSE

print $cgi->end_html;

exit 0;
