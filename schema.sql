CREATE TABLE cafes (id SERIAL PRIMARY KEY, name TEXT, description TEXT, tags TEXT, added TIMESTAMP);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT, role TEXT);