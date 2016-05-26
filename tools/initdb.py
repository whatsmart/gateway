create table user (id INTEGER  PRIMARY KEY, username text UNIQUE, password blob, `group` text,  permission text, token text);
create table device (id integer primary key, uniqid text unique, name text, position text);
create table client (id integer primary key, username text, deviceid text unique, devicename text, platform text);
