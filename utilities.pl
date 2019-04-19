#!/opt/gns/perl/bin/perl

######################################################################
#
# File      : utilities.pl
#
# Author    : Barry Kimelman
#
# Created   : May 20, 2011
#
# Purpose   : Utility routines for CGI scripts.
#
######################################################################

use strict;
use URI::Escape;
use MIME::QuotedPrint;
use MIME::Base64;
use Mail::Sendmail;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

my $left_padding = "20px;";

######################################################################
#
# Function  : generate_select_list
#
# Purpose   : Generate the code for the ip select list.
#
# Inputs    : $_[0] - name of select list HTML item
#             $_[1] - reference to array containing user choices
#             $_[2] - reference to array containing actual values
#             $_[3] - optional background color for selection list
#
# Output    : (none)
#
# Returns   : Generated code representing ip select list
#
# Example   : $list = generate_select_list("list_name",\@choices,\@values,$bgcol);
#
# Notes     : (none)
#
######################################################################

sub generate_select_list
{
	my ( $list_name , $ref_choices , $ref_values , $background_color ) = @_;
	my ( $list , $count , $index );

	$count = scalar @$ref_choices;
	if ( defined $background_color ) {
		$list = "<select style=\"background-color: ${background_color};\" name=\"$list_name\">\n";
	} # IF
	else {
		$list = "<select name=\"$list_name\">\n";
	} # ELSE
	for ( $index = 0 ; $index < $count ; ++$index ) {
		$list .= "<option value=\"" . $$ref_choices[$index] . "\">" .
						$$ref_values[$index] . "</option>\n";
	} # FOR
	$list .= "</select>\n";

	return $list;
} # end of generate_select_list

######################################################################
#
# Function  : generate_select_list_with_font
#
# Purpose   : Generate the code for the ip select list.
#
# Inputs    : $_[0] - name of select list HTML item
#             $_[1] - reference to array containing user choices
#             $_[2] - reference to array containing actual values
#             $_[3] - optional background color for selection list
#
# Output    : (none)
#
# Returns   : Generated code representing ip select list
#
# Example   : $list = generate_select_list_with_font("list_name",\@choices,\@values,$bgcol);
#
# Notes     : (none)
#
######################################################################

sub generate_select_list_with_font
{
	my ( $list_name , $ref_choices , $ref_values , $background_color ) = @_;
	my ( $list , $count , $index );

	$count = scalar @$ref_choices;
	if ( defined $background_color ) {
		$list = "<select class='bigtext' style=\"background-color: ${background_color};\" name=\"$list_name\">\n";
	} # IF
	else {
		$list = "<select class='bigtext' name=\"$list_name\">\n";
	} # ELSE
	for ( $index = 0 ; $index < $count ; ++$index ) {
		$list .= "<option value=\"" . $$ref_choices[$index] . "\">" .
						$$ref_values[$index] . "</option>\n";
	} # FOR
	$list .= "</select>\n";

	return $list;
} # end of generate_select_list_with_font

######################################################################
#
# Function  : generate_select_list_with_font_and_initial
#
# Purpose   : Generate the code for the ip select list.
#
# Inputs    : $_[0] - name of select list HTML item
#             $_[1] - reference to array containing user choices
#             $_[2] - reference to array containing actual values
#             $_[3] - string identifying initially selected choice
#                     (could be an empty string)
#             $_[4] - optional background color for selection list
#
# Output    : (none)
#
# Returns   : Generated code representing ip select list
#
# Example   : $list = generate_select_list_with_font_and_initial("list_name",\@choices,\@values,$initial_choice,$bgcol);
#
# Notes     : (none)
#
######################################################################

sub generate_select_list_with_font_and_initial
{
	my ( $list_name , $ref_choices , $ref_values , $initial_choice , $background_color ) = @_;
	my ( $list , $count , $index , $selected );

	$count = scalar @$ref_choices;
	if ( defined $background_color ) {
		$list = "<select class='bigtext' style=\"background-color: ${background_color};\" name=\"$list_name\">\n";
	} # IF
	else {
		$list = "<select class='bigtext' name=\"$list_name\">\n";
	} # ELSE
	for ( $index = 0 ; $index < $count ; ++$index ) {
		$selected = "";
		if ( $initial_choice ne "" && $initial_choice eq $$ref_choices[$index] ) {
			$selected = " selected='selected'";
		} # IF
		$list .= "<option value=\"" . $$ref_choices[$index] . "\"${selected}>" .
						$$ref_values[$index] . "</option>\n";
	} # FOR
	$list .= "</select>\n";

	return $list;
} # end of generate_select_list_with_font_and_initial

######################################################################
#
# Function  : generate_select_list_with_size
#
# Purpose   : Generate the code for a <SELECT> list.
#
# Inputs    : $_[0] - name of select list HTML item
#             $_[1] - value for title attribute
#             $_[2] - reference to array containing user choices
#             $_[3] - reference to array containing actual values
#             $_[4] - "size" for <SELECT>
#             $_[5] - optional background color for selection list
#
# Output    : (none)
#
# Returns   : Generated code representing ip select list
#
# Example   : $select = generate_select_list_with_size( { 'list_name' => $sitename2_field ,
#						'list_id' => $sitename2_field , 'option_titles' => \%titles ,
#						'title' => 'Site Name' , 'ref_choices' => \@sites ,
#						'ref_values' => \@sites2 , 'size' => 13 , 'bgcolor' => 'wheat' } );
#
# Notes     : (none)
#
######################################################################

sub generate_select_list_with_size
{
	my ( $ref_parms ) = @_;
	my ( $list_name , $list_id , $title , $ref_choices , $ref_values , $bgcolor , $size );
	my ( $list , $count , $index , $ref_option_titles , $style );

	$list_name = $ref_parms->{'list_name'};
	$list_id = $ref_parms->{'list_id'};
	$title = $ref_parms->{'title'};
	$ref_choices = $ref_parms->{'ref_choices'};
	$ref_values = $ref_parms->{'ref_values'};
	$bgcolor = $ref_parms->{'bgcolor'};
	$size = $ref_parms->{'size'};
	$ref_option_titles = $ref_parms->{'option_titles'};

	$style = 'font-family: Courier New, Courier, Arial; ';

	$count = scalar @$ref_choices;
	if ( defined $bgcolor ) {
		$style .= "background-color: ${bgcolor};";
	} # IF
	$list = "<select id='$list_id' title='$title' style='$style' size='${size}' name=\"$list_name\">\n";

	for ( $index = 0 ; $index < $count ; ++$index ) {
		if ( exists $ref_option_titles->{$$ref_choices[$index]} ) {
			$title = ' title="' . $ref_option_titles->{$$ref_choices[$index]} . '" ';
		} # IF
		else {
			$title = ' ';
		} # ELSE
		$list .= "<option ${title}value=\"" . $$ref_choices[$index] . "\">" .
						$$ref_values[$index] . "</option>\n";
	} # FOR
	$list .= "</select>\n";

	return $list;
} # end of generate_select_list_with_size

######################################################################
#
# Function  : list_directory_files
#
# Purpose   : Produce a list of files under a directory.
#
# Inputs    : $_[0] - name of directory
#             $_[1] - reference to array to receive list of files
#             $_[2] - reference to error message buffer
#
# Output    : (none)
#
# Returns   : IF no problems THEN number of files ELSE negative
#
# Example   : $count = list_directory_files($dirname,\@list,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub list_directory_files
{
	my ( $dirname , $ref_list , $ref_errmsg ) = @_;
	my ( %entries , $count );

	$$ref_errmsg = "";
	@$ref_list = ();
	unless ( opendir(DIR,$dirname) ) {
		$$ref_errmsg = "opendir failed for \"$dirname\" : $!";
		return -1;
	} # UNLESS

	%entries = map {  $_ , 0 } readdir DIR;
	closedir DIR;
	delete $entries{".."};
	delete $entries{"."};
	$count = scalar keys %entries;
	@$ref_list = sort { lc $a cmp lc $b } keys %entries;

	return $count;
} # end of list_directory_files

######################################################################
#
# Function  : list_directory_files_with_line_counts
#
# Purpose   : Get a list of files and record counts under a directory.
#
# Inputs    : $_[0] - name of directory
#             $_[1] - reference to hash to receive list of files
#                     (key = filename , value = lines_count)
#             $_[2] - reference to error message buffer
#
# Output    : (none)
#
# Returns   : IF no problems THEN number of files ELSE negative
#
# Example   : $count = list_directory_files_with_line_counts($dirname,\%hash,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub list_directory_files_with_line_counts
{
	my ( $dirname , $ref_hash , $ref_errmsg ) = @_;
	my ( %entries , $count , $path , $buffer );

	$$ref_errmsg = "";
	%$ref_hash = ();
	unless ( opendir(DIR,$dirname) ) {
		$$ref_errmsg = "opendir failed for \"$dirname\" : $!";
		return -1;
	} # UNLESS

	%entries = map {  $_ , -1 } readdir DIR;
	closedir DIR;
	delete $entries{".."};
	delete $entries{"."};
	$count = scalar keys %entries;
	foreach my $entry ( keys %entries ) {
		$path = "${dirname}/${entry}";
		if ( open(LIST,"<$path") ) {
			$entries{$entry} = 0;
			while ( $buffer = <LIST> ) {
				$entries{$entry} += 1;
			} # WHILE
			close LIST;
		} # IF
	} # FOREACH

	%$ref_hash = %entries;

	return $count;
} # end of list_directory_files_with_line_counts

1;
