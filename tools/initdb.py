create table user (id INTEGER  PRIMARY KEY, username text UNIQUE, password blob, `group` text,  permission text, token text);
creacreate table device (id integer primary key, uniqid text unique, name text, position text);
