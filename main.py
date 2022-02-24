
import sqlite3
from turtle import done
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Float
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired,length
import requests

MOVIE_DB_API = 'e4c7eea5b0f602d5c3c4b05687655b99'
MOVIE_DB_URL = 'https://api.themoviedb.org/3/search/movie'
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),unique=True,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(500),nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()
class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


class Form(FlaskForm):
    rating = StringField(label='Your review out of 10')
    review = StringField(label='review')
    submit = SubmitField(label='done')

@app.route("/")
def home():
    all_movie = Movie.query.all()


    return render_template("index.html",movies=all_movie)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    db.session.delete(movie_to_update)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/add',methods=['GET','POST'])
def add():
    form = FindMovieForm()

    if request.method == 'POST':
        params = {
                    'api_key':MOVIE_DB_API,
                    'query':form.title.data
                }
        response = requests.get(url=MOVIE_DB_URL, params=params)
        data = response.json()['results']
        return render_template('select.html',all_data=data)

        
    return render_template('add.html',form=form)

@app.route('/find')
def find_movie():
    movie_id = request.args.get('id')
    if movie_id:
        params = {
            "api_key":MOVIE_DB_API,
            "language":'en-US'
        }
        response = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}', params=params)
        data = response.json()
        image_response = requests.get(url=f'https://api.themoviedb.org/3/movie/{movie_id}/images', params=params)
        image = image_response.json()
        new_movie = Movie(title=data['title'],year=data['release_date'].split('-')[0],description=data["overview"],img_url=f'https://image.tmdb.org/t/p/w500{data["poster_path"]}')
        db.session.add(new_movie)
        db.session.commit()

        return render_template('index.html')


@app.route('/edit', methods=['GET','POST'])
def edit():
    form =Form()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)




if __name__ == '__main__':
    app.run(debug=True)
