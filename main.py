from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField
from wtforms.validators import DataRequired
import requests


API_KEY="d0d5b9fd9d6ebe5a65abd44b3abfdd8a"
movie_list=[]




app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///movie-collection.db"
db=SQLAlchemy(app)
class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),unique=True,nullable=False)
    year=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String(250),nullable=False)
    rating=db.Column(db.Float)
    ranking=db.Column(db.Integer)
    review=db.Column(db.String(100))
    img_url=db.Column(db.String(300),nullable=False)

# with app.app_context():
#     db.create_all()


class EditForm(FlaskForm):
    updated_rating=FloatField(label="Your Rating Out of 10 e.g.7.5",validators=[DataRequired()])
    updated_review=StringField(label="Your Review",validators=[DataRequired()])
    submit=SubmitField(label="Done")

class Addform(FlaskForm):
    movie_title=StringField(label="Movie Title", validators=[DataRequired()])
    submit=SubmitField(label="Add Movie")

@app.route("/")
def home():
    movies_list=db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(movies_list)):
        movies_list[i].ranking = len(movies_list) - i
        db.session.commit()
    return render_template("index.html",movies=movies_list)

@app.route("/edit",methods=['POST','GET'])
def edit():
    edit_details=EditForm()
    if edit_details.validate_on_submit():
        rating=request.form["updated_rating"]
        review=request.form["updated_review"]
        title=request.args.get('title')
        movies_to_update=Movie.query.filter_by(title=title).first()
        movies_to_update.rating=rating
        movies_to_update.review=review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=edit_details)
@app.route("/delete")
def delete():
    id=request.args.get('id')
    movie_to_delete=Movie.query.filter_by(id=id).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add_movie",methods=['POST','GET'])
def add():
    global movie_list
    form=Addform()
    if form.validate_on_submit():
        movie_name=request.form["movie_title"]
        API_TITLE="https://api.themoviedb.org/3/search/movie"
        params={
         "api_key":API_KEY,
         "query":f"{movie_name}"
         }
        response=requests.get(API_TITLE,params=params)
        data=response.json()["results"]
        for item in data:
            title=item["title"]
            released_date=item["release_date"]
            id=item["id"]
            append_dict={
                "title":title,
                "release_date":released_date,
                "id":id
            }
            movie_list.append(append_dict)

        return render_template("select.html",movies_list=movie_list)

    return render_template("add.html",form=form)

@app.route("/app")
def select():
    global movie_list
    movie_id=request.args.get("id")
    API_BY_ID=f"https://api.themoviedb.org/3/movie/{movie_id}"
    params={
         "api_key":API_KEY,
         }
    response=requests.get(API_BY_ID,params=params)
    data=response.json()
    db.create_all()
    new_movie = Movie(
    title=data["original_title"],
    year=data["release_date"][0:4],
    description=data["overview"],
    rating=None,
    ranking=None,
    review=None,
    img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_list.clear()
    return redirect(url_for("edit",title=data["original_title"]))

if __name__ == '__main__':
    app.run(debug=True)
