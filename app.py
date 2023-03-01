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
    return render_template("index.html")

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return redirect("/noexist")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            return redirect("/")
        else:
            return redirect("/incorrect")
    session["username"] = username
    return redirect("/")

@app.route("/register",methods=["POST"])
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
        return redirect("/")
    else:
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