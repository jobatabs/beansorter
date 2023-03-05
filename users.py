import secrets

from flask import session, render_template, redirect

from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from werkzeug.security import check_password_hash, generate_password_hash

from db import db

def login(username: str, password: str):
    sql = text("SELECT id, password, role FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return render_template("error.html", error="User not found.")
    hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["user_id"] = user.id
        session["token"] = secrets.token_hex(16)
        session["role"] = user.role
        return redirect("/")
    return render_template("error.html", error="Incorrect password!")

def register(username: str, password: str):
    hash_value = generate_password_hash(password)
    if len(username) > 50:
        return render_template("error.html", error="Sorry, but that username is too long.")
    if len(password) > 129:
        return render_template("error.html", error="Sorry, but that password is too long.")
    if len(username) < 2:
        return render_template("error.html", \
                                       error="The username must be longer than 1 character")
    if len(password) < 6:
        return render_template("error.html", \
                                       error="The password must be longer than 6 characters.")
    try:
        sql = text("INSERT INTO users (username, password, role) VALUES (:username, :password, 0)")
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
    except IntegrityError:
        return render_template("error.html", \
                                       error="Username has already been taken. \
                                        Please choose another one.")
    return login(username, password)

def invalid_token(token):
    if token != session["token"]:
        return True
    return False

def logout():
    del session["username"]
    del session["user_id"]
    del session["token"]
    del session["role"]

def user_id():
    return session["user_id"]

def is_admin():
    return session["role"] == 1
