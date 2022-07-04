"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods =["GET", "POST"])
def register_user():
    """Register new user"""

    if request.method == "POST":
        #Process form data
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).all()

        if len(user) == 0:
            print('user not found')
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))   
    else:
        return render_template("register_user.html")

@app.route("/login", methods = ["GET", "POST"])
def login_user():
    """Login User"""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).all()[0]

        if user.password == password:
            flash("Logged in.")
            session["user_id"] = user.user_id
            return redirect(url_for('show_user', user_id=user.user_id)) 
        else:
            flash("Incorrect password")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logout."""

    if not session.get("user_id"):
        flash("You are not logged in")
    else:
        session.pop("user_id")
        flash("You are logged out")
    return redirect(url_for("index"))

@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Show user info."""

    user = User.query.filter_by(user_id=user_id).all()[0]
    ratings = db.session.query(Movie, Rating).filter(Movie.movie_id == Rating.movie_id).filter(Rating.user_id==user_id).all()
    return render_template("user.html", user=user, ratings=ratings)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:movie_id>", methods = ["GET", "POST"])
def show_movie(movie_id):
    """Show movie info."""

    if request.method == "POST":
        score = request.form["score"]
        user_id = session.get("user_id")
        user_rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).all()
        if len(user_rating) == 0:
            rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
            db.session.add(rating)
            db.session.commit()
        else:
            user_rating[0].score = score
            db.session.commit()
        return redirect(url_for('show_movie', movie_id=movie_id))
    else:

        movie = Movie.query.filter_by(movie_id=movie_id).all()[0]
        ratings = db.session.query(Movie, Rating).filter(Movie.movie_id == Rating.movie_id).filter(Movie.movie_id==movie_id).all()

        return render_template("movie.html", movie=movie, ratings=ratings)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
