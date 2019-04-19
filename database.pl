#!perl -w

######################################################################
#
# File      : database.pl
#
# Author    : Barry Kimelman
#
# Created   : December 23, 2012
#
# Purpose   : Database support for CGI scripts.
#
######################################################################

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use DBI;
use Time::Local;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

######################################################################
#
# Function  : mysql_connect_to_db
#
# Purpose   : Get a connection to a MySQL database.
#
# Inputs    : $_[0] - name of database (i.e. the schema)
#             $_[1] - name of host (or i.p. address)
#             $_[2] - username
#             $_[3] - password
#             $_[4] - reference to attributes hash
#             $_[5] - reference to error message buffer
#
# Output    : (none)
#
# Returns   : IF success THEN database handle ELSE undefined
#
# Example   : $dbh = mysql_connect_to_db($db,$host,$user,$pwd,\%attr,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub mysql_connect_to_db
{
	my ( $db , $host , $user , $pwd , $ref_attr , $ref_errmsg ) = @_;
	my ( $dbh );

	$$ref_errmsg = '';
	if ( defined $ref_attr ) {
			$dbh = DBI->connect( "DBI:mysql:$db:$host", $user, $pwd, $ref_attr);
	} # IF
	else {
			$dbh = DBI->connect( "DBI:mysql:$db:$host", $user, $pwd);
	} # ELSE
	unless ( $dbh ) {
			$$ref_errmsg = "Error connecting to $db on $host : $DBI::errstr";
			return undef;
	} # UNLESS

	return $dbh;
} # end of mysql_connect_to_db

######################################################################
#
# Function  : count_records_in_table
#
# Purpose   : Count the number of records in a table.
#
# Inputs    : $_[0] - table name
#             $_[1] - reference to array to receive list of column names
#             $_[2] - database handle
#             $_[3] - reference to error message buffer
#
# Output    : appropriate diagnostics
#
# Returns   : IF no problem THEN number of records ELSE negative
#
# Example   : $count = count_records_in_table($table,\@colnames,$dbh,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub count_records_in_table
{
	my ( $table , $ref_colnames , $dbh , $ref_count , $ref_errmsg ) = @_;
	my ( $sql , $sth , $ref , $count , @array );

	$$ref_errmsg = '';
	$sql = "SELECT count(*) FROM ${table};";
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		$$ref_errmsg = "prepare failed for ${sql}<BR>$DBI::errstr<BR>";
		return -1;
	} # UNLESS

	unless ( $sth->execute() ) {
		$$ref_errmsg = "execute failed for ${sql}<BR>$DBI::errstr<BR>";
		$sth->finish();
		return -1;
	} # UNLESS
	$ref = $sth->{'NAME'};
	@$ref_colnames = @$ref;

	$ref = $sth->fetchrow_arrayref();
	unless ( defined $ref ) {
		$$ref_errmsg = "Could not get table count for '$table'<BR>";
		$sth->finish();
		return -1;
	} # UNLESS
	@array = @$ref;
	$count = $array[0];
	$sth->finish();

	return $count;
} # end of count_records_in_table

######################################################################
#
# Function  : get_enum_info_for_table
#
# Purpose   : Describe table.
#
# Inputs    : $_[0] - table name
#             $_[1] - reference to hash to receive info
#             $_[2] - database handle
#             $_[3] - reference to error message buffer
#
# Output    : appropriate diagnostics
#
# Returns   : IF no problem THEN zero ELSE negative
#
# Example   : $status = get_enum_info_for_table($table,\%enum_info,$dbh,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub get_enum_info_for_table
{
	my ( $table , $ref_enum_info , $dbh , $ref_errmsg ) = @_;
	my ( $sql , $sth , $ref , @colnames , @array , $enum , @enum , $count , $index );

	%$ref_enum_info = ();
	$$ref_errmsg = '';

	$sql = "describe $table";
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		$$ref_errmsg = "prepare failed for ${sql}<BR>$DBI::errstr";
		return -1;
	} # UNLESS

	unless ( $sth->execute() ) {
		$$ref_errmsg = "execute failed for ${sql}<BR>$DBI::errstr";
		$sth->finish();
		return -1;
	} # UNLESS

	while ( $ref = $sth->fetchrow_arrayref() ) {
		@array = @$ref;
		if ( $array[1] =~ m/enum/i ) {
			$enum = $array[1];
			$enum =~ s/^enum//g;
			$enum =~ s/^.//g;
			$enum =~ s/.$//g;
			@enum = split(/,/,$enum);
			$count = scalar @enum;
			for ( $index  = 0 ; $index < $count ; ++$index ) {
				$enum[$index] =~ s/^['"]//g;
				$enum[$index] =~ s/['"]$//g;
			} # FOR
			$ref_enum_info->{$array[0]} = [ @enum ];
		} # IF
	} # WHILE

	$sth->finish();

	return 0;
} # end of get_enum_info_for_table

######################################################################
#
# Function  : mysql_describe_table
#
# Purpose   : Print table descriptive information.
#
# Inputs    : $_[0] - tablename
#             $_[1] - database name
#             $_[2] - database handle
#
# Output    : table description
#
# Returns   : nothing
#
# Example   : mysql_describe_table($tablename,$dbname,$dbh);
#
# Notes     : (none)
#
######################################################################

sub mysql_describe_table
{
	my ( $table , $dbname , $dbh ) = @_;
	my ( $sth , $colname , $nullable , $type , $statement , $count , $buffer , $maxlen  );
	my ( $catalog , $schema , $column , $hashref , $col_ref , $enum );
	my ( @colnames , $ref_all_columns , $ref_column );
	my ( $debug1 );

	$catalog = undef;
	$schema = 'qwlc';
	$table = $table;
	$column = "%";
	$sth = $dbh->column_info(undef, $schema, $table, $column);
	$count = 0;

	$hashref = $sth->fetchall_hashref('COLUMN_NAME');
	@colnames = sort { lc $a cmp lc $b } keys %$hashref;

	$statement = <<ENDSQL;
SELECT table_name,column_name,ordinal_position,is_nullable,data_type,character_maximum_length
FROM information_schema.columns
WHERE table_name = '$table' AND table_schema = '$dbname' ORDER BY ordinal_position;
ENDSQL
	print "<BR>mysql_describe_table($table)<BR><PRE>${statement}</PRE><BR><BR>\n";
    
	$sth = $dbh->prepare( $statement );
	unless ( $sth->execute() ) {
		display_error("<BR>describe_table() : failure returned from execute() ; $DBI::errstr<BR>");
		return;
	} # UNLESS

	print qq~
<TABLE border="1" cellspacing="0" cellpadding="2">
<THEAD>
<TR style="background: gainsboro;">
<TH>Ordinal</TH><TH>Column Name</TH>
<TH>Data Type</TH><TH>Maxlen</TH><TH>Nullable?</TH><TH>Enum</TH>
</TR>
</THEAD>
<TBODY>
~;

	$ref_all_columns = $sth->fetchall_hashref('ordinal_position');
	foreach my $ord ( sort { $a <=> $b } keys %$ref_all_columns ) {
		$ref_column = $ref_all_columns->{$ord};

		$nullable = $ref_column->{'is_nullable'};
		$colname = $ref_column->{'column_name'};
		$type = $ref_column->{'data_type'};
		$maxlen = $ref_column->{'character_maximum_length'};
		$col_ref = $hashref->{$colname};
		unless (defined $maxlen) {
			$maxlen = "?";
		} # UNLESS
		if ( $col_ref->{'TYPE_NAME'} eq 'ENUM' ) {
			$enum = join(', ', @{$col_ref->{'mysql_values'}});
		} # IF
		else {
			$enum = "\&nbsp;";
		} # ELSE
		print qq~
<TR>
<TD>$ord</TD><TD>$colname</TD>
<TD>$type</TD><TD>$maxlen</TD><TD>$nullable</TD><TD>$enum</TD>
</TR>
~;
	} # WHILE
	$sth->finish();
	print "</TBODY></TABLE>\n";

	return;
} # end of mysql_describe_table

######################################################################
#
# Function  : mysql_get_columns_info
#
# Purpose   : Get the attributes for a table
#
# Inputs    : $_[0] - tablename
#             $_[1] - database name
#             $_[2] - database handle
#             $_[3] - reference to hash to receive info
#             $_[4] - reference to array to receive list of column names
#             $_[5] - reference to error message buffer
#
# Output    : table description
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = mysql_get_columns_info($tablename,$dbname,$dbh,\%columns,\@colnames,\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub mysql_get_columns_info
{
	my ( $table , $dbname , $dbh , $ref_cols_hash , $ref_cols_list , $ref_errmsg ) = @_;
	my ( $sth , $colname , $nullable , $type , $statement , $count , $buffer , $maxlen  );
	my ( $catalog , $schema , $column , $hashref , $col_ref , $enum );
	my ( @colnames , $ref_all_columns , $ref_column );
	my ( $debug1 );

	%$ref_cols_hash = ();
	@$ref_cols_list = ();
	$$ref_errmsg = "";

	$catalog = undef;
	$schema = 'qwlc';
	$table = $table;
	$column = "%";
	$sth = $dbh->column_info(undef, $schema, $table, $column);
	$count = 0;

	$hashref = $sth->fetchall_hashref('COLUMN_NAME');
	@colnames = sort { lc $a cmp lc $b } keys %$hashref;
	@$ref_cols_list = @colnames;

	$statement = <<ENDSQL;
SELECT table_name,column_name,ordinal_position,is_nullable,data_type,character_maximum_length
FROM information_schema.columns
WHERE table_name = '$table' AND table_schema = '$dbname' ORDER BY ordinal_position;
ENDSQL
    
	$sth = $dbh->prepare( $statement );
	unless ( defined $sth ) {
		$$ref_errmsg = "failure returned from prepare() ; $DBI::errstr";
		return -1;
	} # UNLESS
	unless ( $sth->execute() ) {
		$$ref_errmsg = "failure returned from execute() ; $DBI::errstr";
		return -1;
	} # UNLESS

	$ref_all_columns = $sth->fetchall_hashref('ordinal_position');
	foreach my $ord ( sort { $a <=> $b } keys %$ref_all_columns ) {
		$ref_column = $ref_all_columns->{$ord};

		$nullable = $ref_column->{'is_nullable'};
		$colname = $ref_column->{'column_name'};
		$type = $ref_column->{'data_type'};
		$maxlen = $ref_column->{'character_maximum_length'};
		$col_ref = $hashref->{$colname};
		unless (defined $maxlen) {
			$maxlen = "?";
		} # UNLESS
		if ( $col_ref->{'TYPE_NAME'} eq 'ENUM' ) {
			$enum = join(', ', @{$col_ref->{'mysql_values'}});
		} # IF
		else {
			$enum = "";
		} # ELSE
		$ref_cols_hash->{$colname}{'ord'} = $ord;
		$ref_cols_hash->{$colname}{'data_type'} = $type;
		$ref_cols_hash->{$colname}{'maxlen'} = $maxlen;
		$ref_cols_hash->{$colname}{'nullable'} = $nullable;
		$ref_cols_hash->{$colname}{'enum'} = $enum;

	} # WHILE
	$sth->finish();

	return 0;
} # end of mysql_get_columns_info

######################################################################
#
# Function  : fetch_all_records
#
# Purpose   : Fetch all the records for a table.
#
# Inputs    : $_[0] - name of table
#             $_[1] - database handle
#             $_[2] - reference to hash to recveive data
#             $_[3] - column name to be used as the hash key
#             $_[4] - reference to error message buffer
#             $_[5] - optional order by clause
#
# Output    : appropriate diagnostics
#
# Returns   : IF no problem THEN number of records ELSE negative
#
# Example   : $count = fetch_all_records($table,$dbh,\%data,'column_name',\$errmsg);
#
# Notes     : (none)
#
######################################################################

sub fetch_all_records
{
	my ( $table , $dbh ,$ref_records , $key_field , $ref_errmsg , $order_by ) = @_;
	my ( $sql , $sth , $ref , $count , $status );

	$$ref_errmsg = '';
	%$ref_records = ();

	$sql = "SELECT * FROM ${table}";
	if ( defined $order_by ) {
		$sql .= " " . $order_by;
	} # IF
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		$$ref_errmsg = "prepare failed for ${sql}<BR>$DBI::errstr";
		return -1;
	} # UNLESS

	unless ( $sth->execute() ) {
		$$ref_errmsg = "execute failed for ${sql}<BR>$DBI::errstr";
		$sth->finish();
		return -1;
	} # UNLESS

	$ref = $sth->fetchall_hashref($key_field);
	unless ( defined $ref ) {
		$$ref_errmsg = "fetchall failed for table '$table'<BR>$DBI::errstr";
		$sth->finish();
		return -1;
	} # UNLESS
	$sth->finish();

	$status = scalar keys %$ref;
	%$ref_records = %$ref;

	return $status;
} # end of fetch_all_records

######################################################################
#
# Function  : fetch_all_records_sorted
#
# Purpose   : Fetch all the records for a table.
#
# Inputs    : $_[0] - name of table
#             $_[1] - database handle
#             $_[2] - reference to array to recveive data
#             $_[3] - reference to error message buffer
#             $_[4] - order by clause
#             $_[5] - name of key field
#             $_[6] - ref to array to receive list of key values
#
# Output    : appropriate diagnostics
#
# Returns   : IF no problem THEN number of records ELSE negative
#
# Example   : $count = fetch_all_records_sorted($table,$dbh,\@data,\$errmsg,$order_by,$key,\@keys);
#
# Notes     : (none)
#
######################################################################

sub fetch_all_records_sorted
{
	my ( $table , $dbh ,$ref_records , $ref_errmsg , $order_by , $key , $ref_keys ) = @_;
	my ( $sql , $sth , $ref , $count , $status );

	$$ref_errmsg = '';
	@$ref_records = ();
	@$ref_keys = ();

	$sql = "SELECT * FROM ${table}";
	$sql .= " " . $order_by;
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		$$ref_errmsg = "prepare failed for ${sql}<BR>$DBI::errstr";
		return -1;
	} # UNLESS

	unless ( $sth->execute() ) {
		$$ref_errmsg = "execute failed for ${sql}<BR>$DBI::errstr";
		$sth->finish();
		return -1;
	} # UNLESS
	$count = 0;
	while ( $ref = $sth->fetchrow_hashref() ) {
		$count += 1;
		push @$ref_records,$ref;
		push @$ref_keys,$ref->{$key};
	} # WHILE
	$sth->finish();

	return $count;
} # end of fetch_all_records_sorted

1;
