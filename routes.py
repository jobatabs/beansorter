from flask import render_template, redirect, request, abort

from sqlalchemy.sql import text

from app import app
from db import db

import users

@app.route("/")
def index():
    result = db.session.execute(text("SELECT id, name, description FROM cafes WHERE visible=TRUE"))
    cafes = result.fetchall()
    return render_template("index.html", cafes=cafes)

@app.route("/tags")
def tags():
    result = db.session.execute(text("SELECT id, name FROM tags WHERE visible=TRUE"))
    alltags = result.fetchall()
    return render_template("tags.html", alltags=alltags)

@app.route("/newtag")
def newtag():
    return render_template("newtag.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        query = request.form["text"]
        if len(query) < 1:
            return render_template("error.html", error="Please enter a search term.")
        if len(query) > 50:
            return render_template("error.html", error="Please keep your search term below 50 characters.")
        sql = text("SELECT id, name, description FROM cafes WHERE LOWER(name) LIKE LOWER(:text) OR LOWER(description) LIKE LOWER(:text)")
        result = db.session.execute(sql, {"text":"%"+query+"%"})
        results = result.fetchall()
        return render_template("results.html", results=results)

@app.route("/newcafe")
def newcafe():
    result = db.session.execute(text("SELECT id, name FROM tags WHERE visible=TRUE"))
    alltags = result.fetchall()
    return render_template("newcafe.html", alltags=alltags)

@app.route("/cafe")
def cafe():
    cafe_id = request.args.get("id")
    result = db.session.execute(text(f"SELECT cafes.name, cafes.description, \
                                     cafes.added, cafes.updated, users.username \
                                     FROM cafes, users WHERE cafes.id={cafe_id} \
                                     AND cafes.visible=TRUE AND cafes.added_by = users.id"))
    cafe_listing = result.fetchall()
    result = db.session.execute(text(f"SELECT reviews.id, users.username, \
                                     reviews.review, reviews.added \
                                     FROM reviews, users WHERE cafe_id={cafe_id} \
                                     AND reviews.author = users.id AND visible=TRUE"))
    reviews = result.fetchall()
    result = db.session.execute(text(f"SELECT tags.id, tags.name FROM tags, tagmap, cafes WHERE tagmap.tag_id = tags.id AND tagmap.cafe_id = cafes.id AND cafes.id = {cafe_id}"))
    tag_list = result.fetchall()
    return render_template("cafe.html", cafe=cafe_listing, reviews=reviews, id=cafe_id, tags=tag_list)

@app.route("/tag")
def tag():
    tag_id = request.args.get("id")
    result = db.session.execute(text(f"SELECT tags.id, tags.name FROM tags WHERE tags.id={tag_id} AND tags.visible=TRUE"))
    tag_listing = result.fetchall()
    result = db.session.execute(text(f"SELECT cafes.id, cafes.name, cafes.description FROM tags, tagmap, cafes WHERE tagmap.tag_id = tags.id AND tags.id = {tag_id} AND tagmap.cafe_id = cafes.id AND tags.visible = TRUE AND cafes.visible = TRUE"))
    cafes = result.fetchall()
    return render_template("tag.html", cafes=cafes, id=tag_id, tag=tag_listing)

@app.route("/send", methods=["POST"])
def send():
    if users.invalid_token(request.form["token"]):
        abort(403)
    name = request.form["name"]
    description = request.form["description"]
    if len(name) < 1:
        return render_template("error.html", error="Please enter a name for the café.")
    if len(description) < 1:
        return render_template("error.html", error="Please enter a description for the café.")
    if len(name) > 50:
        return render_template("error.html", error="Sorry, the name you provided is too long.")
    if len(description) > 5000:
        return render_template("error.html", \
                               error="Sorry, please keep your description below 5000 characters.")
    sql = text("INSERT INTO cafes (name, description, visible, added, updated, added_by) \
               VALUES (:name, :description, TRUE, NOW(), NOW(), :user) RETURNING id")
    result = db.session.execute(sql, {"name":name, "description":description, "user":users.user_id()})
    db.session.commit()
    cafe_id = result.fetchone()[0]
    for tag_id in request.form.getlist("tags"):
        sql = text("INSERT INTO tagmap (tag_id, cafe_id) VALUES (:tag_id, :cafe_id)")
        db.session.execute(sql, {"tag_id":tag_id, "cafe_id":cafe_id})
    db.session.commit()
    return redirect("/")

@app.route("/del")
def deletepages():
    return render_template("del.html")

@app.route("/sendreview", methods=["POST"])
def sendreview():
    if users.invalid_token(request.form["token"]):
        abort(403)
    review = request.form["review"]
    author = request.form["author"]
    cafe_id = request.form["cafe_id"]
    if len(review) > 2000:
        return render_template("error.html", \
                               error="Sorry, please keep your review below 2000 characters.")
    if len(review) < 1:
        return render_template("error.html", \
                               error="Please write something before posting your review.")
    sql = text("INSERT INTO reviews (cafe_id, author, review, visible, added) \
               VALUES (:cafe_id, :author, :review, TRUE, NOW())")
    db.session.execute(sql, {"cafe_id":cafe_id, "author":author, "review":review})
    db.session.commit()
    return redirect(f"/cafe?id={cafe_id}")

@app.route("/sendtag", methods=["POST"])
def sendtag():
    if users.invalid_token(request.form["token"]):
        abort(403)
    if users.is_admin():
        name = request.form["name"]
        if len(name) > 20:
            return render_template("error.html", \
                                error="Tag must be shorter than 20 characters.")
        if len(name) < 1:
            return render_template("error.html", \
                                error="Please enter a tag.")
        sql = text("INSERT INTO tags (name, visible) \
                VALUES (:name, TRUE) RETURNING id")
        result = db.session.execute(sql, {"name":name})
        db.session.commit()
        tag_id = result.fetchone()[0]
        return redirect(f"/tag?id={tag_id}")
    return render_template("error.html", \
                                error="You must be an administrator to access this page.")

@app.route("/deltag", methods=["POST"])
def deltag():
    if users.invalid_token(request.form["token"]):
        abort(403)
    if users.is_admin():
        del_id = request.form["id"]
        if len(del_id) < 1:
            return render_template("error.html", \
                                error="Please enter an ID.")
        sql = text("UPDATE tags SET visible=FALSE WHERE tags.id=:del_id")
        db.session.execute(sql, {"del_id":del_id})
        db.session.commit()
        return render_template("error.html", error="Delete successful.")
    return render_template("error.html", \
                                error="You must be an administrator to access this page.")

@app.route("/delreview", methods=["POST"])
def delreview():
    if users.invalid_token(request.form["token"]):
        abort(403)
    if users.is_admin():
        del_id = request.form["id"]
        if len(del_id) < 1:
            return render_template("error.html", \
                                error="Please enter an ID.")
        sql = text("UPDATE reviews SET visible=FALSE WHERE reviews.id=:del_id")
        db.session.execute(sql, {"del_id":del_id})
        db.session.commit()
        return render_template("error.html", error="Delete successful.")
    return render_template("error.html", \
                                error="You must be an administrator to access this page.")

@app.route("/delcafe", methods=["POST"])
def delcafe():
    if users.invalid_token(request.form["token"]):
        abort(403)
    if users.is_admin():
        del_id = request.form["id"]
        if len(del_id) < 1:
            return render_template("error.html", \
                                error="Please enter an ID.")
        sql = text("UPDATE cafes SET visible=FALSE WHERE cafes.id=:del_id")
        db.session.execute(sql, {"del_id":del_id})
        db.session.commit()
        return render_template("error.html", error="Delete successful.")
    return render_template("error.html", \
                                error="You must be an administrator to access this page.")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("error.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return users.login(username, password)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return users.register(username, password)

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
