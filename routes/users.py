from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from models import User

bp = Blueprint("users", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.login(
            email=request.form.get("email"), password=request.form.get("password")
        )
        if user:
            session["user_id"] = user.idUser
            flash("Login efetuado com sucesso")
            return redirect(url_for("home"))
        flash("Email ou password incorretos", "error")
        return redirect(url_for("users.login"))
    return render_template("login.html", title="Login")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sessao terminada")
    return redirect(url_for("home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            user = User.create(dict(request.form))
            db.session.add(user)
            db.session.commit()
            flash("Conta criada com sucesso, faca login")
            return redirect(url_for("users.login"))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("users.register"))
    return render_template("register.html", title="Registar")
