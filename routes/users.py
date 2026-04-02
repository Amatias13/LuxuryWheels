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
            flash("Login efetuado com sucesso", "modal")
            # Redirect to the originating page if a next parameter exists
            next_url = request.args.get("next") or request.form.get("next")
            return redirect(next_url if next_url else url_for("home"))
        flash("Email ou palavra-passe incorretos", "modal-error")
        return redirect(url_for("users.login"))
    return render_template("login.html", title="Login", next=request.args.get("next", ""))


@bp.route("/logout")
def logout():
    session.clear()
    # Use a modal-style flash so frontend can show a modal instead of a banner
    flash("Sessão terminada", "modal")
    return redirect(url_for("home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            # Validate password confirmation
            form = dict(request.form)
            pw = form.get('password')
            pw2 = form.get('re_password')
            if not pw or not pw2 or pw != pw2:
                raise ValueError('Palavras-passe não coincidem')
            # remove re_password before creating
            form.pop('re_password', None)
            user = User.create(form)
            db.session.add(user)
            db.session.commit()
            flash("Conta criada com sucesso; faça login", "modal")
            return redirect(url_for("users.login"))
        except ValueError as e:
            flash(str(e), "modal-error")
            return redirect(url_for("users.register"))
    return render_template("register.html", title="Registar")