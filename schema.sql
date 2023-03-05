CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, role INTEGER);
CREATE TABLE tags (id SERIAL PRIMARY KEY, name TEXT, visible BOOLEAN);
CREATE TABLE cafes (id SERIAL PRIMARY KEY, name TEXT, description TEXT, added TIMESTAMP, updated TIMESTAMP, added_by INTEGER REFERENCES users, visible BOOLEAN);
CREATE TABLE tagmap (id SERIAL PRIMARY KEY, cafe_id INTEGER REFERENCES cafes, tag_id INTEGER REFERENCES tags);
CREATE TABLE reviews (id SERIAL PRIMARY KEY, cafe_id INTEGER REFERENCES cafes, author INTEGER REFERENCES users, review TEXT, added TIMESTAMP, visible BOOLEAN);