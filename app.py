import secrets
import sqlite3
from flask import Flask, abort, flash, redirect, render_template, request, session
import markupsafe

import config
import db
import movies
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    genres = movies.get_genres(movie_id)
    ratings = movies.get_ratings_for_movie(movie_id)
    sql = """
        SELECT c.content, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.movie_id = ?
        ORDER BY c.created_at DESC
    """
    comments = db.query(sql, [movie_id])
    return render_template("show_movie.html", movie=movie, genres=genres, ratings=ratings, comments=comments)

@app.route("/find_movie")
def find_movie():
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html", query=query, results=results)

@app.route("/new_movie")
def new_movie():
    require_login()
    genres = movies.get_all_genres()
    return render_template("new_movie.html", genres=genres)

@app.route("/create_movie", methods=["POST"])
def create_movie():
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    release_year = request.form["release_year"]
    if not release_year.isdigit():
        abort(403)
    user_id = session["user_id"]

    genre_ids = request.form.getlist("genres")
    genre_ids = [int(gid) for gid in genre_ids if gid.isdigit()]

    movies.add_movie(title, description, int(release_year), user_id, genre_ids)
    movie_id = movies.add_movie(title, description, int(release_year), user_id, genre_ids)
    return redirect(f"/movie/{movie_id}")

@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    all_genres = movies.get_all_genres()
    movie_genres = [g["id"] for g in movies.get_genres(movie_id)]

    return render_template("edit_movie.html", movie=movie, all_genres=all_genres, movie_genres=movie_genres)

@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()
    check_csrf()

    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    release_year = request.form["release_year"]
    if not release_year.isdigit():
        abort(403)

    genre_ids = request.form.getlist("genres")
    genre_ids = [int(gid) for gid in genre_ids if gid.isdigit()]

    movies.update_movie(movie_id, title, description, int(release_year), genre_ids)

    return redirect("/movie/" + str(movie_id))

@app.route("/remove_movie/<int:movie_id>", methods=["GET", "POST"])
def remove_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_movie.html", movie=movie)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            movies.remove_movie(movie_id)
            return redirect("/")
        else:
            return redirect("/movie/" + str(movie_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "").strip()
    password2 = request.form.get("password2", "").strip()

    if not username:
        flash("VIRHE: Käyttäjätunnus ei voi olla tyhjä")
        return redirect("/register")

    if not password1 or not password2:
        flash("VIRHE: Salasana ei voi olla tyhjä")
        return redirect("/register")

    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return redirect("/register")
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    flash("Käyttäjä luotu! Kirjaudu sisään.")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

@app.route("/user/<int:user_id>")
def user_page(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    movies_by_user = movies.get_movies_by_user(user_id)
    stats = users.get_user_stats(user_id)
    return render_template("show_user.html", user=user, movies=movies_by_user, stats=stats)

@app.route("/add_rating", methods=["POST"])
def add_rating():
    require_login()
    check_csrf()

    rating = request.form["rating"]
    movie_id = request.form["movie_id"]

    if not rating.isdigit() or not movie_id.isdigit():
        abort(400)

    rating = int(rating)
    if rating < 1 or rating > 5:
        abort(400)

    user_id = session["user_id"]

    sql = """
        INSERT INTO ratings (user_id, movie_id, rating)
        VALUES (?, ?, ?)
    """
    db.execute(sql, [user_id, movie_id, rating])
    return redirect(f"/movie/{movie_id}")

@app.route("/add_comment", methods=["POST"])
def add_comment():
    require_login()
    check_csrf()

    movie_id = request.form.get("movie_id")
    content = request.form.get("content", "").strip()
    if not content:
        flash("Kommentti ei voi olla tyhjä")
        return redirect(f"/movie/{movie_id}")

    sql = "INSERT INTO comments (user_id, movie_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [session["user_id"], movie_id, content])
    return redirect(f"/movie/{movie_id}")
