create table user (id INTEGER  PRIMARY KEY, username text UNIQUE, password blob, `group` text,  permission text, token text);
