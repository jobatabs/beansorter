CREATE TABLE cafes (id SERIAL PRIMARY KEY, name TEXT, description TEXT, added TIMESTAMP, updated TIMESTAMP, added_by INTEGER REFERENCES users, visible BOOLEAN);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT, role INTEGER);
