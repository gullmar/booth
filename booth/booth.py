from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from datetime import datetime
import json

from booth import auth, db, offers as booth_offers


bp = Blueprint("booth", __name__)


@bp.route("/")
def index():
    error, products = db.get_all_products()

    if error:
        flash(error)

    return render_template(
        "booth/index.html",
        products=products or [],
        is_index=True,
    )


@bp.route("/register", methods=("GET", "POST"))
@auth.login_required
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
            error = booth_offers.register_product(product_id, name, description)

        if error and product_id:
            db.delete_product(product_id)

        if not error:
            if product_id:
                error, product_offers = booth_offers.get_offers(product_id)
                if not error and product_offers:
                    for offer in product_offers:
                        db.add_offer(
                            offer["id"],
                            product_id,
                            offer["price"],
                            offer["items_in_stock"],
                        )
            flash(f"Product correctly registered!")
            return redirect(url_for("booth.index"))

    if error:
        flash(error)

    return render_template("booth/register.html", back_url=url_for("booth.index"))


@bp.route("/<product_id>/edit", methods=("GET", "POST"))
@auth.login_required
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

    return render_template(
        "booth/edit.html", back_url=url_for("booth.index"), product=product
    )


@bp.route("/<product_id>/delete", methods=("GET", "POST"))
@auth.login_required
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

    return render_template(
        "booth/delete.html", back_url=url_for("booth.index"), product=product
    )


@bp.route("/<product_id>/offers")
def offers(product_id):
    error, product = db.get_product(product_id)

    product_offers = None
    if not error:
        error, product_offers = db.get_product_offers(product_id)

    if error:
        flash(error)
    if not product or product_offers is None:
        return redirect(url_for("booth.index"))

    return render_template(
        "booth/offers.html",
        back_url=url_for("booth.index"),
        product=product,
        offers=product_offers,
    )


@bp.route("/<product_id>/history")
def history(product_id):
    error, product = db.get_product(product_id)

    price_history = None
    if not error:
        error, price_history = db.get_price_history(product_id)

    if error:
        flash(error)
    if not product or price_history is None:
        return redirect(url_for("booth.index"))

    # Generate chart stringified data
    labels = [
        datetime.fromtimestamp(record["timestamp"]).strftime("%x %X")
        for record in price_history
    ]
    datasets = [
        {
            "label": "Mean price",
            "data": [record["mean_price"] for record in price_history],
        },
        {
            "label": "Minimum price",
            "data": [record["min_price"] for record in price_history],
        },
    ]

    return render_template(
        "booth/history.html",
        back_url=url_for("booth.offers", product_id=product_id),
        product=product,
        labels=json.dumps(labels),
        datasets=json.dumps(datasets)
    )
