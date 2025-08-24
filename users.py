from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    return None

def get_user_stats(user_id):
    sql_movies = "SELECT COUNT(*) as count FROM movies WHERE user_id = ?"
    movies_count = db.query(sql_movies, [user_id])[0]['count']

    sql_ratings = "SELECT ROUND(AVG(r.rating), 2) as avg_rating FROM ratings r WHERE r.user_id = ?"
    avg_rating_res = db.query(sql_ratings, [user_id])

    if not avg_rating_res or avg_rating_res[0]['avg_rating'] is None:
        avg_rating = None
    else:
        avg_rating = float(avg_rating_res[0]['avg_rating'])

    return {
        "movies_count": movies_count,
        "avg_rating": avg_rating
    }
