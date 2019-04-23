/*********************************************************************
*
* File      : create_encrypted.sql
*
* Author    : Barry Kimelman
*
* Created   : January 31, 2019
*
* Purpose   : Create the two tables used by my encryption script
*
* Notes     : (none)
*
*********************************************************************/

create table my_encrypted (
	id				int auto_increment unique,
	modified_date	date not null,
	encrypted_data	varbinary(4096) not null
);

create table my_encrypted_control (
	encrypted_data	varbinary(4096) not null
);
