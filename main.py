from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from pandas import describe_option
from wtforms import StringField, SubmitField, IntegerField, FloatField, URLField
from wtforms.validators import DataRequired, URL
import requests


app = Flask(__name__)
app.config["SECRET_KEY"] = "asdkhga348957ksjdflsdk385305"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie_database_updated.db"
Bootstrap(app)
db = SQLAlchemy(app)


title = None

url = "http://www.omdbapi.com/?i=tt3896198&apikey=3bcd66da"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=True)
    review = db.Column(db.String, nullable=True)
    image = db.Column(db.String, nullable=True)


with app.app_context():
    db.create_all()


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    year = IntegerField("Year", validators=[DataRequired()])
    rating = FloatField("Rating", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    review = StringField("review", validators=[DataRequired()])
    image = URLField("Image", validators=[URL()])
    search_title = SubmitField("Search Title", validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])
    update = SubmitField("Update", validators=[DataRequired()])


@app.route("/")
def home():
    all_movies = Movie.query.all()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    global title
    if request.method == "POST":
        title = request.form["title"]
        params = {
            "s": title
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return render_template("select.html", data=data)
    form = MovieForm()
    return render_template("add.html", movies=form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        movie_id = request.args.get("key")
        global title
        params = {
            "s": title
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        title = data["Search"][int(movie_id)]["Title"]
        rating = request.form["rating"]
        review = request.form["review"]
        description = request.form["description"]
        year = data["Search"][int(movie_id)]["Year"]
        image = data["Search"][int(movie_id)]["Poster"]
        add_movie = Movie(title=title, year=year, rating=rating, description=description, review=review, image=image)
        db.session.add(add_movie)
        db.session.commit()
        return redirect(url_for("home"))
    movie_id = request.args.get("key")
    form = MovieForm()
    return render_template("edit.html", movies=form, key=movie_id)


@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        movie_id = request.args.get("key")
        rating = request.form["rating"]
        review = request.form["review"]
        description = request.form["description"]
        selected_movie = db.session.get(Movie, movie_id)
        selected_movie.rating = rating
        selected_movie.review = review
        selected_movie.description = description
        db.session.commit()
        return redirect(url_for("home"))
    movie_id = request.args.get("key")
    form = MovieForm()
    return render_template("update.html", i=movie_id, movies=form)


@app.route("/delete/<int:key>")
def delete(key):
    selected_movie = db.session.get(Movie, key)
    db.session.delete(selected_movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)