from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from booth import db, offers


bp = Blueprint("booth", __name__)


@bp.route("/")
def index():
    error, products = db.get_all_products()

    if error:
        flash(error)

    return render_template("booth/index.html", products=products or [], is_index=True)


@bp.route("/register", methods=("GET", "POST"))
def register():
    error: str | None = None

    if request.method == "POST":
        product_id = None
        name = request.form["name"]
        description = request.form["description"]

        if not name:
            error = "Name is required."
        if not description:
            error = "Description is required."

        if not error:
            error, product_id = db.register_product(name, description)

        if product_id and not error:
            error = offers.register_product(product_id, name, description)

        if not error:
            flash(f"Product correctly registered!")
            return redirect(url_for("booth.index"))

    if error:
        flash(error)

    return render_template("booth/register.html")


@bp.route("/edit/<product_id>", methods=("GET", "POST"))
def edit(product_id):
    error, product = db.get_product(product_id)

    if error or not product:
        if error:
            flash(error)
        return redirect(url_for("booth.index"))

    if not error and request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        if not name:
            error = "Name is required."
        if not description:
            error = "Description is required."

        if not error:
            error = db.update_product(product_id, name, description)

        if not error:
            flash(f"Product correctly edited!")
            return redirect(url_for("booth.index"))

    if error:
        flash(error)

    return render_template("booth/edit.html", product=product)


@bp.route("/delete/<product_id>", methods=("GET", "POST"))
def delete(product_id):
    if request.method == "POST":
        error = db.delete_product(product_id)

        if not error:
            flash(f"Product correctly deleted!")
            return redirect(url_for("booth.index"))

        flash(error)

    error, product = db.get_product(product_id)

    if error:
        flash(error)
    if product is None:
        return redirect(url_for("booth.index"))

    return render_template("booth/delete.html", product=product)
