#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : encrypted.cgi
#
# Author    : Barry Kimelman
#
# Created   : September 28, 2015
#
# Purpose   : Manage encrypted data table
#
######################################################################

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;
use Time::Local;
use Crypt::CBC;
use Switch;
use File::Spec;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;
use months_days;

require "database.pl";
require "CGI-DUMP-COOKIES.pl";
require "CGI-DUMP-ENV.pl";
require "CGI-DUMP-PARAMETERS.pl";

my $cgi;
my $script_name = "";
my $dbh;
my $encrypted_data_table = 'my_encrypted';
my $encrypted_data_control_table = 'my_encrypted_control';
my %encrypted_data = ();
my $top_level_href;
my $secret_key;
my $dummy_test_string = "DUMMY TEST STRING";
my $backup_dir = "C:\\myusername\\encrypted";
my %parameters;

my $debug_mode = 0;

######################################################################
#
# Function  : debug_print
#
# Purpose   : Display an optional debugging message.
#
# Inputs    : @_ - array of strings comprising error message
#
# Output    : requested error message
#
# Returns   : (nothing)
#
# Example   : debug_print("Hello from here ",$xx);
#
# Notes     : The string "DEBUG : " is prepended to each message
#
######################################################################

sub debug_print
{
	my ( $message );

	if ( $debug_mode ) {
		$message = join("",@_);
		while ( $message =~ m/^\n|^<BR>/ ) {
			$message = $';
			print "<BR>";
		} # WHILE
		print "<span class='debugtext'>DEBUG : ${message}</span>\n";
	} # IF

	return;
} # end of debug_print

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
# Function  : decrypt_table
#
# Purpose   : Decrypt the data in a file.
#
# Inputs    : $_[0] - decryption key
#             $_[1] - reference to hash to receive records
#
# Output    : appropriate diagnostics
#
# Returns   : decrypted data
#
# Example   : $num_records = decrypt_table($secret_key,\%records);
#
# Notes     : (none)
#
######################################################################

sub decrypt_table
{
	my ( $secret_key , $ref_records ) = @_;
	my ( $data , $decrypted , $terminator , $sql , $sth , $ref , $ref_all );
	my ( $count , $encrypted , $num_rows );

	%$ref_records = ();
	$sql =<<SQL;
select count(*) num_rows from $encrypted_data_control_table
SQL
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		display_error("<BR>prepare failed for ${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS
	unless ( $sth->execute() ) {
		display_error("<BR>execute failed for ${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -2;
	} # UNLESS
	$ref = $sth->fetchrow_hashref();
	unless ( defined $ref ) {
		display_error("<BR>fetchall failed for ${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -3;
	} # UNLESS

	if ( $ref->{'num_rows'} <= 0 ) {
		debug_print("<BR>Create control table record<BR>\n");

		$sql =<<SQL;
INSERT INTO ${encrypted_data_control_table}
( encrypted_data ) VALUES ( aes_encrypt('$dummy_test_string','$secret_key') )
SQL
		$num_rows = $dbh->do($sql);
		unless ( defined $num_rows ) {
			display_error("<BR>error executing ${sql}<BR>$DBI::errstr<BR>\n");
			return -5;
		} # UNLESS

		debug_print("<BR>Insert into control table was successfull<BR>\n");
	} # IF
	else {
		$sql =<<SQL;
select aes_decrypt(encrypted_data,'$secret_key') encrypted_data
from ${encrypted_data_control_table}
SQL
		$sth = $dbh->prepare($sql);
		unless ( defined $sth ) {
			display_error("<BR>prepare failed for ${sql}<BR>$DBI::errstr<BR>\n");
			return -6;
		} # UNLESS
		unless ( $sth->execute() ) {
			display_error("<BR>execute failed for ${sql}<BR>$DBI::errstr<BR>\n");
			$sth->finish();
			return -7;
		} # UNLESS
		$ref = $sth->fetchrow_hashref();
		unless ( defined $ref ) {
			display_error("<BR>fetchrow failed for ${sql}<BR>$DBI::errstr<BR>\n");
			$sth->finish();
			return -8;
		} # UNLESS
		$decrypted = $ref->{'encrypted_data'};
		unless ( $decrypted eq $dummy_test_string ) {
			display_error("<BR>Invalid secret key. Mismatch against control data string.<BR>\n");
			$sth->finish();
			return -9;
		} # UNLESS
		$sth->finish();
	} # ELSE

	%$ref_records = ();
	$sql =<<SQL;
select id,modified_date,aes_decrypt(encrypted_data,'$secret_key') encrypted_data
from my_encrypted;
SQL
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		display_error("<BR>prepare failed for ${sql}<BR>$DBI::errstr<BR>\n");
		return -10;
	} # UNLESS
	unless ( $sth->execute() ) {
		display_error("<BR>execute failed for ${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -11;
	} # UNLESS
	$ref_all = $sth->fetchall_hashref("id");
	unless ( defined $ref_all ) {
		display_error("<BR>fetchall_hashref failed for ${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -12;
	} # UNLESS

	$count = scalar keys %$ref_all;
	if ( $count < 1 ) {
		return $count;
	} # IF

	%$ref_records = %$ref_all;
	return $count;
} # end of decrypt_table

######################################################################
#
# Function  : meta1
#
# Purpose   : Perform metadata tests.
#
# Inputs    : (none)
#
# Output    : appropriate diagnostics
#
# Returns   : (nothing)
#
# Example   : meta1();
#
# Notes     : (none)
#
######################################################################

sub meta1
{
	my ( $table );

	mysql_describe_table($encrypted_data_table,'qwlc',$dbh);

	mysql_describe_table($encrypted_data_control_table,'qwlc',$dbh);

	return;
} # end of meta1

######################################################################
#
# Function  : generate_list_all_records_form
#
# Purpose   : Generate the add new submission screen.
#
# Inputs    : (none)
#
# Output    : HTML code for the entering of the secret key
#
# Returns   : nothing
#
# Example   : generate_list_all_records_form();
#
# Notes     : (none)
#
######################################################################

sub generate_list_all_records_form
{
	print qq~
<FORM name="form_name" id="form_name" method="POST" action="${script_name}">
<input type="hidden" name="function" value="display_all_records">

<fieldset class="fieldset2">
<legend class="legend2">Enter Secret Key</legend>

<label class="label2" for="secret_key">Secret Key :\&nbsp;</label>
<input type="password" title="Secret Key" class="input_fieldset1" name="secret_key" id="secret_key" size="20" autofocus />

<BR><BR>
<input type="submit" class="darktext2" value="Display All Records"
onclick="return check_all_fields(form_name);"
/>

</fieldset>
</FORM>
~;

	return;
} # end of generate_list_all_records_form

######################################################################
#
# Function  : generate_backup_records_form
#
# Purpose   : Generate the add new submission screen.
#
# Inputs    : (none)
#
# Output    : HTML code for the entering of the secret key
#
# Returns   : nothing
#
# Example   : generate_backup_records_form();
#
# Notes     : (none)
#
######################################################################

sub generate_backup_records_form
{
	print qq~
<FORM name="form_name" id="form_name" method="POST" action="${script_name}">
<input type="hidden" name="function" value="backup_all_records">

<fieldset class="fieldset2">
<legend class="legend2">Enter Secret Key</legend>

<label class="label2" for="secret_key">Secret Key :\&nbsp;</label>
<input type="password" title="Secret Key" class="input_fieldset1" name="secret_key" id="secret_key" size="20" autofocus />

<BR><BR>
<input type="submit" class="darktext2" value="Backup All Records"
onclick="return check_all_fields(form_name);"
/>

</fieldset>
</FORM>
~;

	return;
} # end of generate_backup_records_form

######################################################################
#
# Function  : generate_add_local_encrypted_data_form
#
# Purpose   : Generate the add new submission screen.
#
# Inputs    : (none)
#
# Output    : HTML code for the entering of the secret key
#
# Returns   : nothing
#
# Example   : generate_add_local_encrypted_data_form();
#
# Notes     : (none)
#
######################################################################

sub generate_add_local_encrypted_data_form
{
	print qq~
<H3>Enter parameters for processing of local encrypted file</H3>
<FORM name="doattach" ENCTYPE="multipart/form-data"
method="POST" action="${script_name}">
<input type="hidden" name="function" value="process_local_encrypted_data">

<fieldset class="fieldset2">
<legend class="legend2">Enter Secret Key</legend>

<label class="label2" for="secret_key">Secret Database Key :\&nbsp;</label>
<input type="password" title="Secret Key" class="input_fieldset1" name="secret_key" id="secret_key" size="40" />

<BR><BR>

<label class="label2" for="local_file_key">Local File Key :\&nbsp;</label>
<input type="password" title="Local File Key" class="input_fieldset1" name="local_file_key" id="local_file_key" size="40" />

<BR><BR>

<label class="label2" for="local_file">Local File Path :\&nbsp;</label>
<input type="text" name="local_file" id="local_file" size="80">

<BR><BR>
<input type="submit" class="darktext2" value="Process Local Encrypted Data"
onclick="return check_all_fields(form_name);"
/>

</fieldset>
</FORM>
~;

	return;
} # end of generate_add_local_encrypted_data_form

######################################################################
#
# Function  : display_all_records
#
# Purpose   : Display all of the records in the encrypted data table
#
# Inputs    : (none)
#
# Output    : requested data and appropriate diagnostics
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : display_all_records();
#
# Notes     : (none)
#
######################################################################

sub display_all_records
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref );
	my ( $actions );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {
		return 0;
	} # IF

	print qq~
<TABLE border="1" cellspacing="0" cellpadding="3">
<THEAD>
<TR class='th'>
<TH>Id</TH>
<TH>Date</TH>
<TH>Data</TH>
<TH>Actions</TH>
</TR>
</THEAD>
<TBODY>
~;

	foreach my $key ( sort { $a <=> $b } keys %records ) {
		$ref = $records{$key};
		$actions =<<ACTIONS;
<div style="width: 160px;">

<div style="float: left; width: 65px;">
<FORM class="button_form" name="data_form_1_$key" id="data_form_1_$key" method="POST" action="${script_name}">
<INPUT type="hidden" id="id" name="id" value="$key" />
<INPUT type="hidden" id="function" name="function" value="delete" />
<INPUT type="hidden" id="secret_key" name="secret_key" value="$secret_key" />
<INPUT type="submit" id="submit1" name="submit1" value="Delete"
onclick="return show_confirm_2(data_form_1_$key,'delete this record');"
/>
</FORM>
</div>

<div style="float: left; width: 65px;">
<FORM class="button_form" name="data_form_2_$key" id="data_form_2_$key" method="POST" action="${script_name}">
<INPUT type="hidden" id="id" name="id" value="$key" />
<INPUT type="hidden" id="function" name="function" value="modify" />
<INPUT type="hidden" id="secret_key" name="secret_key" value="$secret_key" />
<INPUT type="submit" id="submit1" name="submit1" value="Modify"
onclick="return show_confirm_2(data_form_2_$key,'modify this record');"
/>
</FORM>
</div>
</div>
ACTIONS
		print qq~
<TR
onMouseOver="this.style.background='peru';this.style.color='white';this.style.fontWeight=900;return true;"
onMouseOut="this.style.backgroundColor=''; this.style.color='black';this.style.fontWeight=500;"
>
<TD>$key</TD>
<TD>$ref->{'modified_date'}</TD>
<TD>$ref->{'encrypted_data'}</TD>
<TD>${actions}</TD>
</TR>
~;
	} # FOREACH
	print "</TBODY></TABLE>\n";

	return;
} # end of display_all_records

######################################################################
#
# Function  : backup_data
#
# Purpose   : Backup the data
#
# Inputs    : (none)
#
# Output    : requested data and appropriate diagnostics
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : backup_data();
#
# Notes     : (none)
#
######################################################################

sub backup_data
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref );
	my ( $actions , $clock , $filename , $path );
	my ( $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {
		return 0;
	} # IF
	$clock = time;
	( $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst ) =
				localtime($clock);
	$year += 1900;
	$mon += 1;
	$filename = sprintf "encrypted-%02d_%02d_%04d--%02d-%02d-%02d",
					$mon,$mday,$year,$hour,$min,$sec;
	$path = File::Spec->catfile($backup_dir,$filename);
	print "<H3>Backup data will be written to $path</H3>\n";
	unless ( open(BACKUP,">$path") ) {
		display_error("open failed for '$path' : $!<BR>\n");
		return -1;
	} # UNLESS

	foreach my $key ( sort { $a <=> $b } keys %records ) {
		$ref = $records{$key};
		print BACKUP "$ref->{'encrypted_data'}\n";
	} # FOREACH
	close BACKUP;
	display_error("<BR>Please remember to encrypt the backup file<BR>\n");

	return 0;
} # end of backup_data

######################################################################
#
# Function  : process_local_encrypted_data
#
# Purpose   : Add the data from a local encrypted file
#
# Inputs    : (none)
#
# Output    : requested data and appropriate diagnostics
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : process_local_encrypted_data();
#
# Notes     : (none)
#
######################################################################

sub process_local_encrypted_data
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref );
	my ( $actions , $clock , $filename , $path , $local_file_key , $local_file );
	my ( $upload_filehandle , $buffer , $num_encrypted_bytes );
	my ( $cipher , $encrypted_data , $decrypted_data , $count );
	my ( $chunk_size );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret Database key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$local_file_key = $parameters{'local_file_key'};
	unless ( defined $local_file_key ) {
		display_error("<BR>Local File key was not specified<BR>\n");
		return -1;
	} # UNLESS
	$cipher = Crypt::CBC->new(
		-key    => $local_file_key,
		-cipher => 'Blowfish'
	);
	unless ( defined $cipher ) {
		display_error("Could nmot create cipher for local file key : $!<BR>\n");
		return -1;
	} # UNLESS

	$local_file = $parameters{'local_file'};
	unless ( defined $local_file ) {
		display_error("<BR>Local File name was not specified<BR>\n");
		return -1;
	} # UNLESS

	unless ( open(ENCRYPTED,"<$local_file") ) {
		display_error("open failed for '$local_file'<BR>\n");
		return -1;
	} # UNLESS
	## binmode $upload_filehandle;
	##  $num_encrypted_bytes = 0;
	##  $encrypted_data = <$upload_filehandle>;
	##  $num_encrypted_bytes = length $encrypted_data;
	$encrypted_data = <ENCRYPTED>;
	close(ENCRYPTED);
	$num_encrypted_bytes = length $encrypted_data;
	print "<H3>${num_encrypted_bytes} bytes of encrypted data from file '$local_file'</H3>\n";
	$decrypted_data = $cipher->decrypt($encrypted_data);
	if ( defined $decrypted_data ) {
		print "<H3>Decrypted data from local file '$local_file' is<PRE>$decrypted_data</PRE></H3>\n";
	} # IF
	else {
		display_error("Could not decrupty local encrypted file : $!<BR>\n");
	} # ELSE

	return 0;
} # end of process_local_encrypted_data

######################################################################
#
# Function  : query_records
#
# Purpose   : Display all of the records in the encrypted data table
#
# Inputs    : (none)
#
# Output    : requested data and appropriate diagnostics
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : query_records();
#
# Notes     : (none)
#
######################################################################

sub query_records
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref );
	my ( $actions , $query_data , $num_matched );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$query_data = $parameters{'query_data'};
	unless ( defined $query_data ) {
		display_error("<BR>query term was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {
		return 0;
	} # IF
	$num_matched = 0;

	print qq~
<TABLE border="1" cellspacing="0" cellpadding="3">
<THEAD>
<TR class='th'>
<TH>Id</TH>
<TH>Date</TH>
<TH>Data</TH>
<TH>Actions</TH>
</TR>
</THEAD>
<TBODY>
~;

	foreach my $key ( sort { $a <=> $b } keys %records ) {
		$ref = $records{$key};
		if ( $ref->{'encrypted_data'} !~ m/${query_data}/i ) {
			next;
		} # IF
		$num_matched += 1;

		$actions =<<ACTIONS;
<div style="width: 160px;">

<div style="float: left; width: 65px;">
<FORM class="button_form" name="data_form_1_$key" id="data_form_1_$key" method="POST" action="${script_name}">
<INPUT type="hidden" id="id" name="id" value="$key" />
<INPUT type="hidden" id="function" name="function" value="delete" />
<INPUT type="hidden" id="secret_key" name="secret_key" value="$secret_key" />
<INPUT type="submit" id="submit1" name="submit1" value="Delete"
onclick="return show_confirm_2(data_form_1_$key,'delete this record');"
/>
</FORM>
</div>

<div style="float: left; width: 65px;">
<FORM class="button_form" name="data_form_2_$key" id="data_form_2_$key" method="POST" action="${script_name}">
<INPUT type="hidden" id="id" name="id" value="$key" />
<INPUT type="hidden" id="function" name="function" value="modify" />
<INPUT type="hidden" id="secret_key" name="secret_key" value="$secret_key" />
<INPUT type="submit" id="submit1" name="submit1" value="Modify"
onclick="return show_confirm_2(data_form_2_$key,'modify this record');"
/>
</FORM>
</div>
</div>
ACTIONS
		print qq~
<TR>
<TD>$key</TD>
<TD>$ref->{'modified_date'}</TD>
<TD>$ref->{'encrypted_data'}</TD>
<TD>${actions}</TD>
</TR>
~;
	} # FOREACH
	print "</TBODY></TABLE>\n";
	print "<BR><H3>Number of records matching '$query_data' = ${num_matched}</H3><BR>\n";

	return;
} # end of query_records

######################################################################
#
# Function  : modify_record_level_1
#
# Purpose   : First level of record modification
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = modify_record_level_1();
#
# Notes     : (none)
#
######################################################################

sub modify_record_level_1
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref , $id );
	my ( $actions );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {  # This should not be possible
		return 0;
	} # IF
	$id = $parameters{'id'};
	$ref = $records{$id};
	unless ( defined $ref ) {
		display_error("<BR>Could not find record with id = ${id}<BR>\n");
		return -1;
	} # UNLESS

	print qq~
<FORM name="modify_record_form" id="modify_record_form" method="POST" action="${script_name}">
<input type="hidden" name="function" value="modify_record_level_2">
<input type="hidden" name="secret_key" id="secret_key" value="$secret_key">
<input type="hidden" name="id" id="id" value="$id">

<fieldset class="fieldset2">
<legend class="legend2">Enter Information</legend>

<label class="label2" for="new_data">Record Data :\&nbsp;</label>
<input type="text" title="Record Data" class="input_fieldset1" name="modified_data" id="modified_data" size="90" value="$ref->{'encrypted_data'}" />

<BR><BR>
<input type="submit" class="darktext2" value="Modify Record Data"
onclick="return check_all_fields(modify_record_form);"
/>

</fieldset>
</FORM>
~;

	return 0;
} # end of modify_record_level_1

######################################################################
#
# Function  : delete_record_level_1
#
# Purpose   : Delete a record
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = delete_record_level_1();
#
# Notes     : (none)
#
######################################################################

sub delete_record_level_1
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref , $id );
	my ( $num_rows , $sql );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF
	backup_data();

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {  # This should not be possible
		return 0;
	} # IF
	$id = $parameters{'id'};
	$ref = $records{$id};
	unless ( defined $ref ) {
		display_error("<BR>Could not find record with id = ${id}<BR>\n");
		return -1;
	} # UNLESS

	$sql =<<SQL;
DELETE FROM ${encrypted_data_table} WHERE id = ${id}
SQL
	$num_rows = $dbh->do($sql);
	unless ( defined $num_rows ) {
		display_error("<BR>error executing ${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS
	print "<H3>Record was successfully deleted</H3>\n";
	display_all_records();

	return 0;
} # end of delete_record_level_1

######################################################################
#
# Function  : modify_record_level_2
#
# Purpose   : Second level of record modification
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = modify_record_level_2();
#
# Notes     : (none)
#
######################################################################

sub modify_record_level_2
{
	my ( $num_records , $errmsg , $decrypted , %records , $ref , $id );
	my ( $num_rows , $sql , $modified_data );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%records);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt table data<BR>\n");
		return -1;
	} # IF
	backup_data();

	print "<H3>Number of records is $num_records</H3>\n";
	if ( $num_records == 0 ) {  # This should not be possible
		return 0;
	} # IF
	$id = $parameters{'id'};
	$ref = $records{$id};
	unless ( defined $ref ) {
		display_error("<BR>Could not find record with id = ${id}<BR>\n");
		return -1;
	} # UNLESS

	$modified_data = $parameters{'modified_data'};
	$sql =<<SQL;
UPDATE ${encrypted_data_table}
SET encrypted_data = aes_encrypt('$modified_data','$secret_key'),
modified_date = now()
WHERE id = ${id}
SQL
	$num_rows = $dbh->do($sql);
	unless ( defined $num_rows ) {
		display_error("<BR>error executing ${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS
	print "<H3>Record was successfully modified</H3>\n";
	##  display_all_records();

	return 0;
} # end of modify_record_level_2

######################################################################
#
# Function  : generate_add_record_screen
#
# Purpose   : Generate the add record screen
#
# Inputs    : (none)
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_add_record_screen();
#
# Notes     : (none)
#
######################################################################

sub generate_add_record_screen
{
	my ( $buffer );

	$buffer = localtime;

	print qq~
<FORM name="new_record_form" id="new_record_form" method="POST" action="${script_name}">
<input type="hidden" name="function" value="add_new_record">

<fieldset class="fieldset2">
<legend class="legend2">Enter Information</legend>

<label class="label2" for="secret_key">Secret Key :\&nbsp;</label>
<input type="password" title="Secret Key" class="input_fieldset1" name="secret_key" id="secret_key" size="20" autofocus />

<BR><BR>
<label class="label2" for="new_data">Record Data :\&nbsp;</label>
<input type="text" title="Record Data" class="input_fieldset1" name="new_data" id="new_data" size="90" />

<BR><BR>
<input type="submit" class="darktext2" value="Add New Record"
onclick="return check_all_fields(new_record_form);"
/>

</fieldset>
</FORM>
~;

	return;
} # end of generate_add_record_screen

######################################################################
#
# Function  : generate_query_record_screen
#
# Purpose   : Generate the query records screen
#
# Inputs    : (none)
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_query_record_screen();
#
# Notes     : (none)
#
######################################################################

sub generate_query_record_screen
{
	my ( $buffer );

	$buffer = localtime;

	print qq~
<FORM name="query_record_form" id="query_record_form" method="POST" action="${script_name}">
<input type="hidden" name="function" value="query_records">

<fieldset class="fieldset2">
<legend class="legend2">Enter Query Information</legend>

<label class="label2" for="secret_key">Secret Key :\&nbsp;</label>
<input type="password" title="Secret Key" class="input_fieldset1" name="secret_key" id="secret_key" size="20" autofocus />

<BR><BR>
<label class="label2" for="query_data">Query Term :\&nbsp;</label>
<input type="text" title="Record Data" class="input_fieldset1" name="query_data" id="query_data" size="90" />

<BR><BR>
<input type="submit" class="darktext2" value="Search Records"
onclick="return check_all_fields(query_record_form);"
/>

</fieldset>
</FORM>
~;

	return;
} # end of generate_query_record_screen

######################################################################
#
# Function  : add_new_record
#
# Purpose   : Display all of the records in the encrypted data table
#
# Inputs    : (none)
#
# Output    : requested data and appropriate diagnostics
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : add_new_record();
#
# Notes     : (none)
#
######################################################################

sub add_new_record
{
	my ( $errmsg , $sql , $sth , $new_data , $num_records );
	my ( %decrypted , $num_rows );

	$secret_key = $parameters{'secret_key'};
	unless ( defined $secret_key ) {
		display_error("<BR>Secret key was not specified<BR>\n");
		return -1;
	} # UNLESS
	$new_data = $parameters{'new_data'};
	unless ( defined $new_data ) {
		display_error("<BR>New data was not specified<BR>\n");
		return -1;
	} # UNLESS

	$num_records = decrypt_table($secret_key,\%decrypted);
	if ( $num_records < 0 ) {
		display_error("<BR>Could not decrypt existing data ($num_records)<BR>\n");
		return -1;
	} # IF
	backup_data();

	$sql =<<SQL;
INSERT INTO ${encrypted_data_table} ( modified_date , encrypted_data )
VALUES ( now() , aes_encrypt('$new_data','$secret_key') )
SQL
	$num_rows = $dbh->do($sql);
	unless ( defined $num_rows ) {
		display_error("<BR>error executing ${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS

	print "<H3>Record containing '$new_data' successfully inserted</H3>\n";

	return;
} # end of add_new_record

######################################################################
#
# Function  : generate_menu_entry
#
# Purpose   : Generate an entry for the main commands menu
#
# Inputs    : $_[0] - menu title
#             $_[1] - command function word
#
# Output    : main menu entry
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_menu_entry("Add New Entry","addsub1");
#
# Notes     : (none)
#
######################################################################

sub generate_menu_entry
{
	my ( $menu_title , $function_word ) = @_;
	my ( $form_name , $div_name );

	$form_name = "form_${function_word}";
	$div_name = "div_${function_word}";
	print qq~
<BR>
<FORM name="${form_name}" id="${form_name}" method="POST" action="${script_name}">
<input type="hidden" name="function" value="${function_word}">
<input class="submit1" type="submit" value="$menu_title">
</FORM>
~;

	return;
} # end of generate_menu_entry

######################################################################
#
# Function  : generate_main_screen
#
# Purpose   : Generate the main screen
#
# Inputs    : (none)
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_main_screen();
#
# Notes     : (none)
#
######################################################################

sub generate_main_screen
{
	my ( $buffer );

	$buffer = localtime;
	print qq~
<div style="padding-left: 20px;">
<H3>${buffer}</H3>
~;
	generate_menu_entry("List Data","listall");
	generate_menu_entry("Query Data","query");
	generate_menu_entry("Add New Record","add");
	generate_menu_entry("List Metadata","meta");
	generate_menu_entry("Backup Data","backup");
	generate_menu_entry("Add Local Encrypted Data","add_local_encrypted_data");
	print "</div>\n";

	return;
} # end of generate_main_screen

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

my ( @fields , $function , $func , $style , $title , $count , $ref );
my ( $buffer , $status , $errmsg , $errors , $errmsg2 );

$script_name = $ENV{"SCRIPT_NAME"};
@fields = split(/\//,$script_name);
$script_name = $fields[$#fields];
$top_level_href = "<A class='boldlink3' HREF='${script_name}'>Return to Main Screen</A>";

$cgi = new CGI;
$title = "Encrypted Data Management";
print $cgi->header;

print $cgi->start_html(
			-title => "$title" ,
			-style=>[
				{-src=>'/styles.css'},
				{-src=>'/fieldset.css'}
			],
			-script=>[
				{-type=>'javascript', -src=>'/check_all_fields.js'},
				{-type=>'javascript', -src=>'/hide_show_divider.js'} ,
				{-type=>'javascript', -src=>'/show_confirm_2.js'} ,
				{-type=>'javascript', -src=>'/show_confirm.js'}
			]
		);

print $cgi->h1("$title");
%parameters = map { $_ , $cgi->param($_) } $cgi->param();

##  cgi_dump_script_parameters($cgi,"CGI script parameters");

#-- Connect to database --#
debug_print("Connect to database<BR>");
$dbh = mysql_connect_to_db("qwlc","127.0.0.1","username","password",undef,\$errmsg);
unless ( defined $dbh ) {
	display_error($errmsg);
	print $cgi->end_html;
	exit 0;
} # UNLESS

$function = $parameters{'function'};
if ( defined $function && $function =~ m/\S/ ) {
	$function =~ s/ /./g;
	switch ( $function ) {
		case 'add_local_encrypted_data' {
			generate_add_local_encrypted_data_form();
		}
		case 'process_local_encrypted_data' {
			process_local_encrypted_data();
		}
		case 'listall' {
			generate_list_all_records_form();
		}
		case 'display_all_records' {
			display_all_records();
		}
		case 'backup' {
			generate_backup_records_form();
		}
		case 'backup_all_records' {
			backup_data();
		}
		case 'query_records' {
			query_records();
		}
		case 'query' {
			generate_query_record_screen();
		}
		case 'add' {
			generate_add_record_screen();
		}
		case 'add_new_record' {
			add_new_record();
		}
		case 'delete' {
			delete_record_level_1();
		}
		case 'modify' {
			modify_record_level_1();
		}
		case 'modify_record_level_2' {
			modify_record_level_2();
		}
		case 'meta' {
			meta1();
		}
		else {
			display_error("<BR>Received request for unsupported function '$function'<BR>\n");
		}
	} # SWITCH
	print "<BR>$top_level_href<BR><BR><BR><BR>\n";
} # IF
else {
	generate_main_screen();
} # ELSE

if ( $dbh ) {
	$dbh->disconnect();
} # IF

print $cgi->end_html;

exit 0;
