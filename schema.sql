CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    release_year INTEGER,
    user_id INTEGER REFERENCES users
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE
);

CREATE TABLE movie_genres (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    genre_id INTEGER REFERENCES genres
);

CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    user_id INTEGER REFERENCES users,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5)
);