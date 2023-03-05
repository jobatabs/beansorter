from flask import render_template, redirect, request, abort

from sqlalchemy.sql import text

from app import app
from db import db

import users

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

@app.route("/send", methods=["POST"])
def send():
    if users.invalid_token(request.form["token"]):
        abort(403)
    name = request.form["name"]
    description = request.form["description"]
    sql = text("INSERT INTO cafes (name, description) VALUES (:name, :description)")
    db.session.execute(sql, {"name":name, "description":description})
    db.session.commit()
    return redirect("/")

@app.route("/sendreview", methods=["POST"])
def sendreview():
    if users.invalid_token(request.form["token"]):
        abort(403)
    review = request.form["review"]
    author = request.form["author"]
    cafe_id = request.form["cafe_id"]
    sql = text("INSERT INTO reviews (cafe_id, author, review) \
               VALUES (:cafe_id, :author, :review)")
    db.session.execute(sql, {"cafe_id":cafe_id, "author":author, "review":review})
    db.session.commit()
    return redirect(f"/cafe?id={cafe_id}")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("error.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        match users.login(username, password):
            case 0:
                return redirect("/")
            case 1:
                return render_template("error.html", error="User not found.")
            case 2:
                return render_template("error.html", error="Incorrect password!")
            case 3:
                return render_template("error.html", error="Username has already been taken. Please choose another one.")
            case _:
                return render_template("error.html", error="Unexpected error. Guru meditation time")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        match users.register(username, password):
            case 0:
                return redirect("/")
            case 1:
                return render_template("error.html", error="User not found.")
            case 2:
                return render_template("error.html", error="Incorrect password!")
            case 3:
                return render_template("error.html", error="Username has already been taken. Please choose another one.")
            case _:
                return render_template("error.html", error="Unexpected error. Guru meditation time")
        

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
