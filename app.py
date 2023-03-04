from os import getenv

from flask import Flask
from flask import render_template, redirect, request, session

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import text

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute(text("SELECT id, name, description FROM cafes"))
    cafes = result.fetchall()
    return render_template("index.html", cafes=cafes)

@app.route("/newcafe")
def newcafe():
    return render_template("newcafe.html")

@app.route("/cafe")
def cafe():
    cafe_id = request.args.get("id")
    result = db.session.execute(text(f"SELECT name, description FROM cafes WHERE id={cafe_id}"))
    cafe_listing = result.fetchall()
    result = db.session.execute(text(f"SELECT users.username, reviews.review FROM reviews, users \
                                     WHERE cafe_id={cafe_id} AND reviews.author = users.id"))
    reviews = result.fetchall()
    return render_template("cafe.html", cafe=cafe_listing, reviews=reviews, id=cafe_id)

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/send", methods=["POST"])
def send():
    name = request.form["name"]
    description = request.form["description"]
    sql = text("INSERT INTO cafes (name, description) VALUES (:name, :description)")
    db.session.execute(sql, {"name":name, "description":description})
    db.session.commit()
    return redirect("/")

@app.route("/sendreview", methods=["POST"])
def sendreview():
    review = request.form["review"]
    author = request.form["author"]
    cafe_id = request.form["cafe_id"]
    sql = text("INSERT INTO reviews (cafe_id, author, review) \
               VALUES (:cafe_id, :author, :review)")
    db.session.execute(sql, {"cafe_id":cafe_id, "author":author, "review":review})
    db.session.commit()
    return redirect(f"/cafe?id={cafe_id}")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return redirect("/noexist")
    hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["user_id"] = user.id
        return redirect("/")
    return redirect("/incorrect")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        hash_value = generate_password_hash(password)
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        session["username"] = username
        sql = text("SELECT id FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        session["user_id"] = user.id
        return redirect("/")
    return redirect("/exists")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/incorrect")
def incorrect():
    return render_template("incorrect.html")

@app.route("/exists")
def exists():
    return render_template("exists.html")

@app.route("/noexist")
def noexist():
    return render_template("noexist.html")
