import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from booth import db


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if not error:
            password_hash = generate_password_hash(password)
            error = db.add_user(username, password=password_hash)

        if not error:
            flash("User registered correctly! Now you can login.")
            return redirect(url_for("auth.login"))

    if error:
        flash(error)

    return render_template(
        "auth/register.html", session_control=True, back_url=url_for("booth.index")
    )


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error, user = db.get_user(username=username)

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if not error and user:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

    if error:
        flash(error)

    return render_template(
        "auth/login.html", session_control=True, back_url=url_for("booth.index")
    )


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        error, user = db.get_user(id=user_id)
        if not error and user:
            g.user = user


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
