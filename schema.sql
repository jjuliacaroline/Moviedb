CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    release_year INTEGER,
    user_id INTEGER REFERENCES users
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_genres (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    genre_id INTEGER REFERENCES genres
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    user_id INTEGER REFERENCES users,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5)
);