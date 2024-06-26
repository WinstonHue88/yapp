from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import binascii

from yapp.db import get_db
from yapp.encrypt import encrypt_with_option, decrypt_with_option

bp = Blueprint("user", __name__)

@bp.route("/")
def index():
    db = get_db()
    users = db.execute("SELECT name FROM users")

    return render_template("user/index.html", users=users)


@bp.route("/sign-up", methods=("GET", "POST"))
def sign_up():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        password_confirmation = request.form["password_confirmation"]
        option = request.form["encrypt_option"]

        db = get_db()

        if password != password_confirmation:
            flash("Password should be equal to password confirmation", "error")
        elif db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone():
            flash("Username already exist.", "error")
        else:
            encrypted_password = encrypt_with_option(password, option).decode("latin-1")
            db.execute(
                "INSERT INTO users (name, username, password, encrypted_password, encrypted_by)"
                "VALUES (?, ?, ?, ?, ?)",
                (name, username, password, encrypted_password, option)
            )
            db.commit()
            flash("Successful created user", "notice")
            return redirect(url_for("index"))
    return render_template("user/sign-up.html")


@bp.route("/sign-in", methods=("GET", "POST"))
def sign_in():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            flash("Username does not exist", "error")
            return render_template("user/sign-in.html")

        option = user["encrypted_by"]
        decrypted_password = str(decrypt_with_option(user["encrypted_password"].encode("latin-1"), option))
        if password != decrypted_password:
            flash("Incorrect password", "error")
        else:
            flash("Successful sign in", "notice")
            return redirect(url_for("index"))
    return render_template("user/sign-in.html")

