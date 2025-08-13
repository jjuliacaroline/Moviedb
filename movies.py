import db

def get_all_genres():
    sql = "SELECT id, title FROM genres ORDER BY id"
    return db.query(sql)    

def add_movie(title, description, release_year, user_id, genre_ids):
    sql = "INSERT INTO movies (title, description, release_year, user_id) VALUES (?, ?, ?, ?)"
    curr = db.execute(sql, [title, description, release_year, user_id])
    movie_id = curr.lastrowid

    sql = "INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)"
    for gid in genre_ids:
        db.execute(sql, [movie_id, gid])
    return movie_id

def get_movies():
    sql = """
        SELECT m.id, m.title, m.description, m.release_year, m.user_id, u.username,
               COUNT(r.id) as rating_count
        FROM movies m
        LEFT JOIN users u ON m.user_id = u.id
        LEFT JOIN ratings r ON m.id = r.movie_id
        GROUP BY m.id, m.title, m.description, m.release_year, m.user_id, u.username
        ORDER BY m.title
    """
    movies = db.query(sql)

    for movie in movies:
        movie['genres'] = get_genres_for_movie(movie['id'])
        movie['avg_rating'] = get_avg_rating_for_movie(movie['id'])

    return movies

def get_movie(movie_id):
    sql = "SELECT id, title, description, release_year, user_id FROM movies WHERE id = ?"
    result = db.query(sql, [movie_id])
    if not result:
        return None
    movie = result[0]
    movie['genres'] = get_genres_for_movie(movie_id)
    movie['avg_rating'] = get_avg_rating_for_movie(movie_id)
    return movie

def get_genres_for_movie(movie_id):
    sql = """
        SELECT g.title
        FROM genres g
        JOIN movie_genres mg ON g.id = mg.genre_id
        WHERE mg.movie_id = ?
    """
    rows = db.query(sql, [movie_id])
    return ", ".join(row['title'] for row in rows) if rows else ""

def get_avg_rating_for_movie(movie_id):
    sql = "SELECT AVG(rating) as avg_rating FROM ratings WHERE movie_id = ?"
    result = db.query(sql, [movie_id])
    return round(result[0]['avg_rating'], 2) if result and result[0]['avg_rating'] else None

def update_movie(movie_id, title, description, release_year, genre_ids):
    sql = "UPDATE movies SET title = ?, description = ?, release_year = ? WHERE id = ?"
    db.execute(sql, [title, description, release_year, movie_id])

    sql = "DELETE FROM movie_genres WHERE movie_id = ?"
    db.execute(sql, [movie_id])

    sql = "INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)"
    for gid in genre_ids:
        db.execute(sql, [movie_id, gid])

def remove_movie(movie_id):
    sql = "DELETE FROM movie_genres WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM ratings WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM comments WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])

def get_genres(movie_id):
    sql = """
        SELECT g.id, g.title
        FROM genres g
        JOIN movie_genres mg ON g.id = mg.genre_id
        WHERE mg.movie_id = ?
    """
    return db.query(sql, [movie_id])

def find_movies(query):
    like_query = "%" + query + "%"
    sql = """
        SELECT id, title, description, release_year, user_id
        FROM movies
        WHERE title LIKE ?
        ORDER BY title
    """
    movies = db.query(sql, [like_query])
    for movie in movies:
        movie['genres'] = get_genres_for_movie(movie['id'])
        movie['avg_rating'] = get_avg_rating_for_movie(movie['id'])
    return movies

def get_ratings_for_movie(movie_id):
    sql = """
        SELECT r.rating, r.user_id, u.username
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = ?
    """
    return db.query(sql, [movie_id])

def get_movies_by_user(user_id):
    sql = """
    SELECT id, title, description, release_year, user_id
    FROM movies
    WHERE user_id = ?
    ORDER BY title
    """
    movies = db.query(sql, [user_id])
    for movie in movies:
        movie['genres'] = get_genres_for_movie(movie['id'])
        movie['avg_rating'] = get_avg_rating_for_movie(movie['id'])
    return movies