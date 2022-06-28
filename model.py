"""Models and database functions for Ratings project."""
import os
from dotenv import load_dotenv

load_dotenv()

from flask_sqlalchemy import SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    @classmethod
    def get_by_id(cls, user_id):
        """Get a user from database by ID and return instance."""

        QUERY = """SELECT user_id, email, password
                   FROM users WHERE user_id = :id"""
        cursor = db.session.execute(QUERY, {'id': user_id})
        user_id, email, password = cursor.fetchone()
        return cls(user_id, email, password)

    def change_password(self, password):
        """Change password for the user."""

        QUERY = ("UPDATE users SET password = :password " +
                 "WHERE user_id = :id")
        db.session.execute(QUERY, {'password': password,
                                   'id': self.user_id})
        db.session.commit()

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} email={self.email}>"

# Put your Movie and Rating model classes here.


##############################################################################
# Helper functions

class Movie(db.Model):
    """movies in ratings website"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(200))
    released_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(200))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Movie movie_id={self.movie_id} title={self.title}>"

        
class Rating(db.Model):

    __tablename__ ="ratings"

    rating_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    score = db.Column(db.Integer)

    # Define relationship to user
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Rating rating_id={self.rating_id} 
                movie_id={self.movie_id} 
                user_id={self.user_id} 
                score={self.score}>"""



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database 
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
