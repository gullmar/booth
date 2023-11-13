import sqlite3
from uuid import uuid4

import click
from flask import current_app, g

from booth import constants


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        script = f.read().decode("utf-8")
        print("sql script", script)
        db.executescript(script)


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# Model


def register_product(name, description):
    error = None
    product_id = str(uuid4())

    try:
        db = get_db()
        db.execute(
            "INSERT INTO products (id, name, description) VALUES (?, ?, ?)",
            (product_id, name, description),
        )
        db.commit()
    except sqlite3.IntegrityError:
        error = f'Name "{name}" is already used by another product.'
    except Exception:
        error = constants.GENERIC_ERROR_MESSAGE

    if error:
        product_id = None

    return error, product_id


def get_all_products():
    error, products = None, None

    try:
        products = (
            get_db()
            .execute("SELECT id, name, description FROM products ORDER BY name")
            .fetchall()
        )

        if products is None:
            error = "Error retrieving products."
    except Exception:
        error = constants.GENERIC_ERROR_MESSAGE

    return error, products


def get_product(id):
    error, product = None, None

    try:
        product = (
            get_db()
            .execute(
                "SELECT id, name, description FROM products WHERE id = ?",
                (id,),
            )
            .fetchone()
        )

        if product is None:
            error = f"Product id {id} does not exist"
    except Exception:
        error = constants.GENERIC_ERROR_MESSAGE

    return error, product


def update_product(id, name, description):
    error = None

    try:
        db = get_db()
        db.execute(
            "UPDATE products SET name = ?, description = ? WHERE id = ?",
            (name, description, id),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        error = f'Name "{name}" is already used by another product.'
    except Exception:
        error = constants.GENERIC_ERROR_MESSAGE

    return error


def delete_product(id):
    error = None

    try:
        db = get_db()
        db.execute("DELETE FROM products WHERE id = ?", (id,))
        db.commit()
    except Exception:
        error = constants.GENERIC_ERROR_MESSAGE

    return error
